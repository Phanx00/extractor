## Extractor
A script for extract JS function name from a list of url


- -i -- input file

- -c -- Cookie

- -s -- Seconds

### Usage

```
python3 extractor.py -i <input-file> <-c key1=value1;key2=valu2;> <-s 1>
```

### Example of output:

```json
{
"https://example/test.js": [
  "chgCursor",
  "chgStyleSrc",
  "chgStyleBackSrc",
  "getWindowW",
  "getWindowH",
  "getPopupW",
  "getPopupH",
  "showNumber",
  "showNumberBold",
  "trim",
  "ReorderOrSwapFirstAndLastColumn",
  "LoadColumnsLists",
  "gridCreated",
  "_requestStart",
  "onResponseEnd",
  "showRadWin",
  "showRadModal",
  "onClientClose",
  "getRadWindow",
  "showFilters",
  "detailCustomer",
  "doWindowOpen",,
  "trackCount",
  "limitText",
  "openNotes",
  "selColor",
  "openDetailProduct",
  "doHelp"
 ],
 "https://example/home.aspx": [
  "onLoad",
  "formOnSubmit",
  "wndsize"
 ],
   ...
}
```
