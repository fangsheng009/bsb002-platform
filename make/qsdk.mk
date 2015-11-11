QSDK_DIR=$(TOP_DIR)/qsdk
QSDK_BUILD_DIR=$(QSDK_DIR)/build_dir
FEED_CONFIGS=$(wildcard $(TOP_DIR)/*/feeds.conf)
MERGE_FEEDS=$(MAKE_TOOLS_DIR)/mergeFeeds.py

# All qsdk targets are located in the 
vpath qsdk.% $(QSDK_BUILD_DIR)

define done
	mkdir -p $(QSDK_BUILD_DIR)
	touch $(QSDK_BUILD_DIR)/$@
endef

qsdk.%: $(QSDK_BUILD_DIR)

$(QSDK_BUILD_DIR):
	echo $(@D)

qsdk.merge-feeds: $(FEED_CONFIGS)
	mkdir -p $(QSDK_BUILD_DIR)
	-mv $(QSDK_BUILD_DIR)/feeds.conf.pristine $(QSDK_DIR)/feeds.conf
	$(MERGE_FEEDS) -q $(QSDK_DIR) $^ -o $(QSDK_BUILD_DIR)/feeds.conf.merge-feeds
	mv $(QSDK_DIR)/feeds.conf $(QSDK_BUILD_DIR)/feeds.conf.pristine
	mv $(QSDK_BUILD_DIR)/feeds.conf.merge-feeds $(QSDK_DIR)/feeds.conf
	$(MAKE) -C $(QSDK_DIR) package/symlinks
	mv $(QSDK_DIR)/feeds.conf $(QSDK_BUILD_DIR)/feeds.conf.merge-feeds
	mv $(QSDK_BUILD_DIR)/feeds.conf.pristine $(QSDK_DIR)/feeds.conf
	$(call done)

qsdk/world: qsdk.merge-feeds
