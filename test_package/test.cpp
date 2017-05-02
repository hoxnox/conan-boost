#include <boost/filesystem.hpp>
#include <string.h>
#include <stdio.h>

int main(int argc, char* argv[])
{
	if (boost::filesystem::exists(argv[0]))
		return 0;
	return -1;
}

