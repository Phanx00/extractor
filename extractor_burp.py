# -*- coding: utf-8 -*-
from burp import IBurpExtender, ITab, IHttpListener
from javax.swing import (
    JPanel, JButton, JTextArea, JScrollPane, BoxLayout, JLabel, JTable, SwingUtilities, JTextField
)
from javax.swing.table import DefaultTableModel, TableRowSorter
from javax.swing.RowFilter import regexFilter
from java.lang import Runnable
from javax.swing.event import DocumentListener
import re
import hashlib
from bs4 import BeautifulSoup
from java.awt import Dimension

# Filtri globali
exclude_type = [
    "text/kendo-template"
]

exclude_ext = [
    ".jpg",
    ".png",
    ".css",
    ".map",
    ".pdf"
]

exclude_file = [
    "jquery",
    "moment",
    "bootstrap",
    "chart",
    "gauge"
]


exclude_content = [ 
    "image",
    "font",
    "pdf",
    "css",
    "octet-stream"
   ]

class BurpExtender(IBurpExtender, ITab, IHttpListener):

    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName("JS Function Finder")

        self.hashes_seen = set()

        # GUI
        self.panel = JPanel()
        self.panel.setLayout(BoxLayout(self.panel, BoxLayout.Y_AXIS))

        self.label = JLabel("Monitored URLs (JS functions found):")
        self.panel.add(self.label)

        # Barra di ricerca
        self.searchField = JTextField(10)
        self.searchField.setMaximumSize(Dimension(300, 50))
        self.searchField.setToolTipText("Function filter")
        self.searchField.getDocument().addDocumentListener(self.SearchFilter(self))
        self.panel.add(self.searchField)

        self.tableModel = DefaultTableModel(["URL", "Function"], 0)
        self.resultTable = JTable(self.tableModel)

        self.sorter = TableRowSorter(self.tableModel)
        self.resultTable.setRowSorter(self.sorter)

        self.panel.add(JScrollPane(self.resultTable))

        callbacks.registerHttpListener(self)
        callbacks.addSuiteTab(self)

    def getTabCaption(self):
        return "JS Finder"

    def getUiComponent(self):
        return self.panel

    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):
        if messageIsRequest:
            return

        responseInfo = self._helpers.analyzeResponse(messageInfo.getResponse())
        content_type = None

        for header in responseInfo.getHeaders():
            if header.lower().startswith("content-type"):
                content_type = header.lower()
                break

        if not content_type or any(x in content_type for x in exclude_content):
            return

        full_url = self._helpers.analyzeRequest(messageInfo).getUrl().toString()
        normalized_url = full_url.split('?', 1)[0].split('#', 1)[0].lower()

        # Esclusioni per estensione e nome file
        if any(normalized_url.endswith(ext) for ext in exclude_ext):
            return
        if any(f in normalized_url for f in exclude_file):
            return

        body = messageInfo.getResponse()[responseInfo.getBodyOffset():]
        content = self._helpers.bytesToString(body)

        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        if content_hash in self.hashes_seen:
            return
        self.hashes_seen.add(content_hash)

        patterns = [
          r"function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(",
          r"([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*function\s*\(",
          r"([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\([^)]*\)\s*=>"
        ]

        functions = []

        try:
            if ".js" in normalized_url or "javascript" in content_type:
                for pat in patterns:
                   functions += re.findall(pat, content)
            else:
                soup = BeautifulSoup(content, "html.parser")
                for script in soup.find_all("script"):
                    script_type = script.get("type", "").lower()
                    if not script.get("src") and script_type not in exclude_type:
                        for pat in patterns:
                            functions += re.findall(pat, script.text)
        except Exception as e:
            functions = ["Error during analysis: %s" % str(e)]
    

        if functions:
            SwingUtilities.invokeLater(lambda: self.updateTable(normalized_url, functions))

    def updateTable(self, url, functions):
        self.tableModel.addRow([url, functions[0]])
        for f in functions[1:]:
            self.tableModel.addRow(["", f])

    class SearchFilter(DocumentListener):
        def __init__(self, outer):
            self.outer = outer

        def insertUpdate(self, e): self.updateFilter()
        def removeUpdate(self, e): self.updateFilter()
        def changedUpdate(self, e): self.updateFilter()

        def updateFilter(self):
            text = self.outer.searchField.getText().strip()
            if not text:
                self.outer.sorter.setRowFilter(None)
            else:
                try:
                    self.outer.sorter.setRowFilter(regexFilter("(?i).*%s.*" % re.escape(text), 1))
                except:
                    self.outer.sorter.setRowFilter(None)
