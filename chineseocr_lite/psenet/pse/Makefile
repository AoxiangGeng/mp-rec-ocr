CXXFLAGS = -I include -std=c++11 -O3 $(shell python3-config --cflags)
UNAME := $(shell uname)
ifeq ($(UNAME), Darwin)
	LDSTACK = -Wl,-stack_size,1000000
	TMPFLAGS = $(shell python3-config --ldflags)
	LDFLAGS := $(filter-out $(LDSTACK), $(TMPFLAGS))
	DEPS = $(shell find include -xtype f)
else
	LDFLAGS = $(shell python3-config --ldflags)
	DEPS = $(shell find include -xtype f)
endif

CXX_SOURCES = pse.cpp

LIB_SO = pse.so

$(LIB_SO): $(CXX_SOURCES) $(DEPS)
	$(CXX) -o $@ $(CXXFLAGS) $(LDFLAGS) $(CXX_SOURCES) --shared -fPIC

clean:
	rm -rf $(LIB_SO)