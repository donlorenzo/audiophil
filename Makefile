PYTHON = python3
RESOURCE_DIR = resources
SOURCE_DIR = src/audiophil
UI_SOURCE_FILES = audiophil.ui configDlg.ui mediaLibrary.ui
UI_TARGET_FILES = $(UI_SOURCE_FILES:%.ui=ui_%.py)
RESOURCE_FILE = audiophil.qrc
RESOURCE_TARGET = $(RESOURCE_FILE:%.qrc=%_rc.py)

.PHONY: all clean

all: audiophil $(UI_TARGET_FILES) $(RESOURCE_TARGET)

audiophil: setup.py
	$(PYTHON) setup.py build

ui_%.py: $(RESOURCE_DIR)/%.ui
	pyuic4 $< > $(SOURCE_DIR)/$@

$(RESOURCE_TARGET): $(RESOURCE_DIR)/$(RESOURCE_FILE)
	pyrcc4 $< > $(SOURCE_DIR)/$@

install:
	$(PYTHON) setup.py install

clean:
	-rm $(SOURCE_DIR)/ui_*
	-rm $(SOURCE_DIR)/*.pyc
	-rm $(SOURCE_DIR)/$(RESOURCE_TARGET)
	-rm -rf build/
