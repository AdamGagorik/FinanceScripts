################################################################################
CLEAN=find . \
          -type d -name .ipynb_checkpoints -or \
          -type d -name .pytest_cache -or \
          -type d -name __pycache__ -or \
          -type f -name \*.pyc

################################################################################
define __help_message__
[targets]
    make help  : show this message
    make clean : show some files to remove
    make force : actually remove the files
endef
export __help_message__

################################################################################
.PHONY : help
help:
	@echo "$$__help_message__"

################################################################################
.PHONY : clean
clean:
	-$(CLEAN)

################################################################################
.PHONY : force
force:
	-$(CLEAN) | xargs -I xxx rm -rvf xxx
