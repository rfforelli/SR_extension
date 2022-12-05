#### BE CAREFUL: You may not need to edit this Makefile. ####

ifndef V
	QUIET_AR            = @echo 'MAKE:' AR $@;
	QUIET_BUILD         = @echo 'MAKE:' BUILD $@;
	QUIET_C             = @echo 'MAKE:' CC $@;
	QUIET_CXX           = @echo 'MAKE:' CXX $@;
	QUIET_CHECKPATCH    = @echo 'MAKE:' CHECKPATCH $(subst .o,.cpp,$@);
	QUIET_CHECK         = @echo 'MAKE:' CHECK $(subst .o,.cpp,$@);
	QUIET_LINK          = @echo 'MAKE:' LINK $@;
	QUIET_CP            = @echo 'MAKE:' CP $@;
	QUIET_MKDIR         = @echo 'MAKE:' MKDIR $@;
	QUIET_MAKE          = @echo 'MAKE:' MAKE $@;
	QUIET_INFO          = @echo -n 'MAKE:' INFO '';
	QUIET_RUN           = @echo 'MAKE:' RUN '';
	QUIET_CLEAN         = @echo 'MAKE:' CLEAN ${PWD};
endif

all:
	@echo "INFO: make <TAB> for targets"
.PHONY: all

CXX          = g++
TARGET_ARCH = linux64

INCDIR :=
INCDIR += -I$(MODEL_DIR)/py
INCDIR += -I$(MODEL_DIR)/firmware/nnet_utils/
INCDIR += -I$(MODEL_DIR)/firmware/ap_types/
INCDIR += -I$(MODEL_DIR)/firmware
INCDIR += -I$(MODEL_DIR)/firmware/weights
INCDIR += -I$(XILINX_VIVADO)/include

CXX_FLAGS :=
CXX_FLAGS += -MMD
CXX_FLAGS += -Wall
CXX_FLAGS += -Wno-int-in-bool-context
CXX_FLAGS += -Wno-uninitialized
CXX_FLAGS += -Wno-unknown-pragmas
CXX_FLAGS += -Wno-unused-label
CXX_FLAGS += -Wno-sign-compare
CXX_FLAGS += -Wno-unused-variable
CXX_FLAGS += -Wno-narrowing
CXX_FLAGS += -std=c++11
CXX_FLAGS += -O3

# Define the following MACROs to load weights/biases from file.
WEIGHTS_DIR := $(MODEL_DIR)/firmware/weights
CXX_FLAGS += -D__WEIGHTS_DIR__=$(WEIGHTS_DIR)

LD_FLAGS :=
LD_FLAGS += -lm

LD_LIBS :=

VPATH :=
VPATH += $(MODEL_DIR)
VPATH += $(MODEL_DIR)/py
VPATH += $(MODEL_DIR)/firmware
VPATH += $(MODEL_DIR)/firmware/weights
VPATH += $(MODEL_DIR)/nnet_utils

CXX_SOURCES :=
#CXX_SOURCES += $(subst $(MODEL_DIR)/,,$(wildcard $(MODEL_DIR)/*.cpp))
CXX_SOURCES += myproject_test.cpp
CXX_SOURCES += $(subst $(MODEL_DIR)/firmware/,,$(wildcard $(MODEL_DIR)/firmware/*.cpp))

.SUFFIXES: .cpp .h .o

trim-trailing-space:
	@echo "INFO: Remove trailing spaces from $(DATA_FILE)"
	@sed --in-place 's/[[:space:]]\+$$//' $(DATA_FILE)
.PHONY: trim-trailing-space

dat2jpg:
	@python ./dat2jpg.py $(DATA_FILE) $(IMG_FILE)
.PHONY: dat2jpg

CXX_OBJECTS := $(CXX_SOURCES:.cpp=.o)
-include $(CXX_OBJECTS:.o=.d)

$(MODEL): $(CXX_OBJECTS)
	$(QUIET_LINK)$(CXX) -o $@ $(CXX_OBJECTS) ${LD_LIBS} ${LD_FLAGS}

.cpp.o:
	$(QUIET_CXX)$(CXX) $(CXX_FLAGS) ${INCDIR} -c $<

run: $(MODEL)
	$(QUIET_RUN)./$(MODEL) | tee run.log
.PHONY: run

generate-image: trim-trailing-space dat2jpg
.PHONY: generate-image

show-image: generate-image
	eog $(IMG_FILE)
.PHONY: show-image

#valgrind:
#	$(QUIET_RUN)valgrind --leak-check=full --show-leak-kinds=all --track-origins=yes ./$(MODEL)
#.PHONY: valgrind

#gdb:
#	$(QUIET_RUN)gdb ./$(MODEL)
#.PHONY: gdb

clean:
	$(QUIET_CLEAN)rm -rf $(MODEL)
	$(QUIET_CLEAN)rm -f *.o *.d *.log *.dat *.jpg
.PHONY: clean

#ultraclean: clean
#	$(QUIET_CLEAN)rm -rf ./tb_data/*.log *.log *.png ./tb_data/*.mem
#.PHONY: ultraclean
