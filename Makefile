TOP_DIR=..
MAKE_DIR=make
MAKE_TOOLS_DIR=$(MAKE_DIR)/tools

.PHONY : all
all: qsdk/world

include make/qsdk.mk

.PHONY : print-%
print-%:
	@echo "$*=$($*)"