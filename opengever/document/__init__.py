from zope.i18nmessageid import MessageFactory
import mimetypes

_ = MessageFactory('opengever.document')

# For the common MS office formats, see
# http://blogs.msdn.com/b/vsofficedeveloper/archive/2008/05/08/office-2007-open-xml-mime-types.aspx

# MindJet MindManager
mimetypes.add_type('application/vnd.mindjet.mindmanager', '.mmap')

# MS Visio
mimetypes.add_type('application/vnd.visio', '.vsd')
mimetypes.add_type('application/vnd.visio', '.vss')
mimetypes.add_type('application/vnd.visio', '.vst')
mimetypes.add_type('application/vnd.visio', '.vsw')
mimetypes.add_type('application/vnd.visio', '.vdx')
mimetypes.add_type('application/vnd.visio', '.vsx')
mimetypes.add_type('application/vnd.visio', '.vtx')
mimetypes.add_type('application/vnd.visio', '.vsl')

# Adobe InDesign
mimetypes.add_type('application/x-indesign', '.ind')
mimetypes.add_type('application/x-indesign', '.indd')

# Adobe Photoshop
mimetypes.add_type('image/vnd.adobe.photoshop', '.psd')

# Adobe Illustrator
mimetypes.add_type('application/illustrator', '.ai')

# MS Project
mimetypes.add_type('application/vnd.ms-project', '.mpp')

# MS Project (generic)
mimetypes.add_type('application/x-project', '.mpt')
mimetypes.add_type('application/x-project', '.mpv')
mimetypes.add_type('application/x-project', '.mpx')

# MS Excel
mimetypes.add_type('application/vnd.ms-excel', '.xls')
mimetypes.add_type('application/vnd.ms-excel', '.xlt')
mimetypes.add_type('application/vnd.ms-excel', '.xla')
mimetypes.add_type('application/vnd.ms-excel', '.xlb')
mimetypes.add_type('application/vnd.ms-excel', '.xlc')
mimetypes.add_type('application/vnd.ms-excel', '.xld')
mimetypes.add_type('application/vnd.ms-excel', '.xll')
mimetypes.add_type('application/vnd.ms-excel', '.xlm')
mimetypes.add_type('application/vnd.ms-excel', '.xlw')

# MS Excel Spreadsheet (OOXML)
mimetypes.add_type('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', '.xlsx')

# MS Excel Spreadsheet (Macro Enabled)
mimetypes.add_type('application/vnd.ms-excel.sheet.macroEnabled.12', '.xlsm')

# MS Excel Template (OOXML)
mimetypes.add_type('application/vnd.openxmlformats-officedocument.spreadsheetml.template', '.xltx')

# MS Excel Template (Macro Enabled)
mimetypes.add_type('application/vnd.ms-excel.template.macroEnabled.12', '.xltm')

# MS Excel Addin (Macro Enabled)
mimetypes.add_type('application/vnd.ms-excel.addin.macroEnabled.12', '.xlam')

# MS Excel Spreadsheet (Binary, Macro Enabled)
mimetypes.add_type('application/vnd.ms-excel.sheet.binary.macroEnabled.12', '.xlsb')


# MS Word
mimetypes.add_type('application/msword', '.doc')
mimetypes.add_type('application/msword', '.wiz')
mimetypes.add_type('application/msword', '.dot')

# MS Word Document (OOXML)
mimetypes.add_type('application/vnd.openxmlformats-officedocument.wordprocessingml.document', '.docx')

# MS Word Document (Macro Enabled)
mimetypes.add_type('application/vnd.ms-word.document.macroEnabled.12', '.docm')

# MS Word Template (OOXML)
mimetypes.add_type('application/vnd.openxmlformats-officedocument.wordprocessingml.template', '.dotx')

# MS Word Template (Macro Enabled)
mimetypes.add_type('application/vnd.ms-word.template.macroEnabled.12', '.dotm')

# MS Powerpoint
mimetypes.add_type('application/vnd.ms-powerpoint', '.ppt')
mimetypes.add_type('application/vnd.ms-powerpoint', '.pot')
mimetypes.add_type('application/vnd.ms-powerpoint', '.pps')
mimetypes.add_type('application/vnd.ms-powerpoint', '.ppa')
mimetypes.add_type('application/vnd.ms-powerpoint', '.pwz')
mimetypes.add_type('application/vnd.ms-powerpoint', '.ppz')

# MS Powerpoint Presentation (OOXML)
mimetypes.add_type('application/vnd.openxmlformats-officedocument.presentationml.presentation', '.pptx')

# MS Powerpoint Template (OOXML)
mimetypes.add_type('application/vnd.openxmlformats-officedocument.presentationml.template', '.potx')

# MS Powerpoint Slideshow (OOXML)
mimetypes.add_type('application/vnd.openxmlformats-officedocument.presentationml.slideshow', '.ppsx')

# MS Powerpoint Addin (Macro Enabled)
mimetypes.add_type('application/vnd.ms-powerpoint.addin.macroEnabled.12', '.ppam')

# MS Powerpoint Presentation (Macro Enabled)
mimetypes.add_type('application/vnd.ms-powerpoint.presentation.macroEnabled.12', '.pptm')

# MS Powerpoint Template (Macro Enabled)
mimetypes.add_type('application/vnd.ms-powerpoint.presentation.macroEnabled.12', '.potm')

# MS Powerpoint Slideshow (Macro Enabled)
mimetypes.add_type('application/vnd.ms-powerpoint.slideshow.macroEnabled.12', '.ppsm')
