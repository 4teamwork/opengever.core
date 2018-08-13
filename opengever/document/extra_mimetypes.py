import mimetypes


def register_additional_mimetypes():
    """Register some additional well-known MIME types to help server-side
    file format recognition do a better job.
    """
    for mimetype, extension in ADDITIONAL_TYPES:
        mimetypes.add_type(mimetype, extension)


ADDITIONAL_TYPES = [
    # For the common MS office formats, see
    # http://blogs.msdn.com/b/vsofficedeveloper/archive/2008/05/08/office-2007-open-xml-mime-types.aspx

    # MindJet MindManager
    ('application/vnd.mindjet.mindmanager', '.mmap'),

    # MS Visio
    ('application/vnd.visio', '.vsd'),
    ('application/vnd.visio', '.vss'),
    ('application/vnd.visio', '.vst'),
    ('application/vnd.visio', '.vsw'),
    ('application/vnd.visio', '.vdx'),
    ('application/vnd.visio', '.vsx'),
    ('application/vnd.visio', '.vtx'),
    ('application/vnd.visio', '.vsl'),

    # Adobe InDesign
    ('application/x-indesign', '.ind'),
    ('application/x-indesign', '.indd'),

    # Adobe Photoshop
    ('image/vnd.adobe.photoshop', '.psd'),

    # Adobe Illustrator
    ('application/illustrator', '.ai'),

    # MS Project
    ('application/vnd.ms-project', '.mpp'),

    # MS Publisher
    ('application/x-mspublisher', '.pub'),

    # MS OneNote
    ('application/onenote', '.one'),

    # MS Project (generic)
    ('application/x-project', '.mpt'),
    ('application/x-project', '.mpv'),
    ('application/x-project', '.mpx'),

    # MS Excel
    ('application/vnd.ms-excel', '.xls'),
    ('application/vnd.ms-excel', '.xlt'),
    ('application/vnd.ms-excel', '.xla'),
    ('application/vnd.ms-excel', '.xlb'),
    ('application/vnd.ms-excel', '.xlc'),
    ('application/vnd.ms-excel', '.xld'),
    ('application/vnd.ms-excel', '.xll'),
    ('application/vnd.ms-excel', '.xlm'),
    ('application/vnd.ms-excel', '.xlw'),

    # MS Excel Spreadsheet (OOXML)
    ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', '.xlsx'),

    # MS Excel Spreadsheet (Macro Enabled)
    ('application/vnd.ms-excel.sheet.macroEnabled.12', '.xlsm'),

    # MS Excel Template (OOXML)
    ('application/vnd.openxmlformats-officedocument.spreadsheetml.template', '.xltx'),

    # MS Excel Template (Macro Enabled)
    ('application/vnd.ms-excel.template.macroEnabled.12', '.xltm'),

    # MS Excel Addin (Macro Enabled)
    ('application/vnd.ms-excel.addin.macroEnabled.12', '.xlam'),

    # MS Excel Spreadsheet (Binary, Macro Enabled)
    ('application/vnd.ms-excel.sheet.binary.macroEnabled.12', '.xlsb'),

    # MS Outlook
    ('application/vnd.ms-outlook', '.msg'),

    # MS Word
    ('application/msword', '.doc'),
    ('application/msword', '.wiz'),
    ('application/msword', '.dot'),

    # MS Word Document (OOXML)
    ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', '.docx'),

    # MS Word Document (Macro Enabled)
    ('application/vnd.ms-word.document.macroEnabled.12', '.docm'),

    # MS Word Template (OOXML)
    ('application/vnd.openxmlformats-officedocument.wordprocessingml.template', '.dotx'),

    # MS Word Template (Macro Enabled)
    ('application/vnd.ms-word.template.macroEnabled.12', '.dotm'),

    # MS Powerpoint
    ('application/vnd.ms-powerpoint', '.ppt'),
    ('application/vnd.ms-powerpoint', '.pot'),
    ('application/vnd.ms-powerpoint', '.pps'),
    ('application/vnd.ms-powerpoint', '.ppa'),
    ('application/vnd.ms-powerpoint', '.pwz'),
    ('application/vnd.ms-powerpoint', '.ppz'),

    # MS Powerpoint Presentation (OOXML)
    ('application/vnd.openxmlformats-officedocument.presentationml.presentation', '.pptx'),

    # MS Powerpoint Template (OOXML)
    ('application/vnd.openxmlformats-officedocument.presentationml.template', '.potx'),

    # MS Powerpoint Slideshow (OOXML)
    ('application/vnd.openxmlformats-officedocument.presentationml.slideshow', '.ppsx'),

    # MS Powerpoint Addin (Macro Enabled)
    ('application/vnd.ms-powerpoint.addin.macroEnabled.12', '.ppam'),

    # MS Powerpoint Presentation (Macro Enabled)
    ('application/vnd.ms-powerpoint.presentation.macroEnabled.12', '.pptm'),

    # MS Powerpoint Template (Macro Enabled)
    ('application/vnd.ms-powerpoint.presentation.macroEnabled.12', '.potm'),

    # MS Powerpoint Slideshow (Macro Enabled)
    ('application/vnd.ms-powerpoint.slideshow.macroEnabled.12', '.ppsm'),

    # Apple Keynote
    ('application/x-iwork-keynote-sffkey', '.key'),

    # Apple pages
    ('application/x-iwork-pages-sffpages', '.pages'),

    # Apple numbers
    ('application/x-iwork-numbers-sffnumbers', '.numbers'),

    # Plain text
    ('text/plain', '.ini'),
]
