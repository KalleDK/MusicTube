BIN_NAME := you.py
CONF_NAME := you.conf
DESTDIR = /
INSTALL_PREFIX = usr/local
.SUFFIXES:
INSTALL = install
INSTALL_PROGRAM = $(INSTALL)
INSTALL_DATA = $(INSTALL) -m 664
INSTALL_DIR = $(INSTALL) -m 774
RM = -rm

.PHONY: install
install:
	@echo "Installing to $(DESTDIR)$(INSTALL_PREFIX)/bin"
	@$(INSTALL_PROGRAM) $(BIN_NAME) $(DESTDIR)$(INSTALL_PREFIX)/bin
	@$(INSTALL_DATA) $(CONF_NAME) $(DESTDIR)$(INSTALL_PREFIX)/etc
	@$(INSTALL_DIR) -d $(DESTDIR)$(INSTALL_PREFIX)/you/completed
	@$(INSTALL_DIR) -d $(DESTDIR)$(INSTALL_PREFIX)/you/tagged
	@$(INSTALL_DIR) -d $(DESTDIR)$(INSTALL_PREFIX)/you/raw
	@$(INSTALL_DIR) -d $(DESTDIR)$(INSTALL_PREFIX)/you/converted
	@$(INSTALL_DIR) -d $(DESTDIR)$(INSTALL_PREFIX)/you/jobs
	@$(INSTALL_DATA) jobs $(DESTDIR)$(INSTALL_PREFIX)/you/jobs

.PHONY: deinstall
deinstall:
	@echo "Removing $(DESTDIR)$(INSTALL_PREFIX)/bin/$(BIN_NAME)"
	@$(RM) $(DESTDIR)$(INSTALL_PREFIX)/bin/$(BIN_NAME)
	@$(RM) $(DESTDIR)$(INSTALL_PREFIX)/etc/$(CONF_NAME)
	@$(RM) -rf $(DESTDIR)$(INSTALL_PREFIX)/you
