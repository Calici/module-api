import module_api.API.lock as lock
from .common import \
    v1_ProgressField, \
    v1_TimeField, \
    Messages, \
    DisplayStatus, \
    ControlConfig, \
    v1_SmartBoxes

class PDFFile(lock.LockSection):
    pdfFile = lock.LockField(type = str, default = '')
    version = lock.LockField(type = int, default = 0)

    def set_pdf(self, file_path : str):
        self.set(
            pdfFile = file_path, 
            version = self.version.get() + 1
        )

class ComponentWithPDFViewer(lock.LockSection):
    version = lock.LockField(type = str, default = '0.0')
    progress = v1_ProgressField()
    messages = Messages()
    status = lock.LockField[DisplayStatus](str, default = 'INIT')
    controls = ControlConfig()
    time = v1_TimeField()
    pdf_file = lock.LockField(type = str, default = "")
    smartBoxes = v1_SmartBoxes(default = [])