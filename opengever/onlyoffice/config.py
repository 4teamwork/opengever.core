TEXT_TYPES = set([
    '.djvu',
    '.doc',
    '.docm',
    '.docx',
    '.dot',
    '.dotm',
    '.dotx',
    '.epub',
    '.fodt',
    '.htm',
    '.html',
    '.mht',
    '.odt',
    '.ott',
    '.pdf',
    '.rtf',
    '.txt',
    '.xps',
])

SPREADSHEET_TYPES = set([
    '.csv',
    '.fods',
    '.ods',
    '.ots',
    '.xls',
    '.xlsm',
    '.xlsx',
    '.xlt',
    '.xltm',
    '.xltx',
])

PRESENTATION_TYPES = set([
    '.fodp',
    '.odp',
    '.otp',
    '.pot',
    '.potm',
    '.potx',
    '.pps',
    '.ppsm',
    '.ppsx',
    '.ppt',
    '.pptm',
    '.pptx',
])

SUPPORTED_TYPES = TEXT_TYPES.union(SPREADSHEET_TYPES).union(PRESENTATION_TYPES)
