QSDK_DIR=$(TOP_DIR)/qsdk
QSDK_BUILD_DIR=$(QSDK_DIR)/build_dir
FEED_CONFIGS=$(wildcard $(TOP_DIR)/*/feeds.conf)
MERGE_FEEDS=$(MAKE_TOOLS_DIR)/mergeFeeds.py

# All qsdk targets are located in the 
vpath qsdk.% $(QSDK_BUILD_DIR)

qsdk.%: $(QSDK_BUILD_DIR)

$(QSDK_BUILD_DIR):
	echo $(@D)

qsdk.merge-feeds: $(FEED_CONFIGS)
	-mv $(QSDK_DIR)/feeds.conf.pristine $(QSDK_DIR)/feeds.conf
	$(MERGE_FEEDS) -q $(QSDK_DIR) $^ -o $(QSDK_DIR)/feeds.conf.merge-feeds
	mv $(QSDK_DIR)/feeds.conf $(QSDK_DIR)/feeds.conf.pristine
	mv $(QSDK_DIR)/feeds.conf.merge-feeds $(QSDK_DIR)/feeds.conf
	$(MAKE) -C $(QSDK_DIR) package/symlinks V=s
	mv $(QSDK_DIR)/feeds.conf $(QSDK_DIR)/feeds.conf.merge-feeds
	mv $(QSDK_DIR)/feeds.conf.pristine $(QSDK_DIR)/feeds.conf
	touch $@

qsdk/world: qsdk.merge-feeds
