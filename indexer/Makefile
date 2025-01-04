# Compiler and flags
CXX = g++
CXXFLAGS = -std=c++17 -Wall

# File names
SRCS = indexer.cpp map_reduce.cpp
HEADERS = map_reduce.hpp
OBJS = $(SRCS:.cpp=.o)
EXEC = indexer

# Default target to build the executable
all: $(EXEC)

# Link the object files to create the executable
$(EXEC): $(OBJS)
	$(CXX) $(OBJS) -o $(EXEC)

# Compile .cpp files into .o files
%.o: %.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Clean up generated files
clean:
	rm -f $(OBJS) $(EXEC)

# Rebuild everything
rebuild: clean all

