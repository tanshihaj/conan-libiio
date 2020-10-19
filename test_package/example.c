#ifdef __APPLE__
#include <iio/iio.h>
#else
#include <iio.h>
#endif
#include <stdio.h>

int main (int argc, char **argv) {
	unsigned int i, j, major, minor;
	char git_tag[8];
	iio_library_get_version(&major, &minor, git_tag);
	printf("Library version: %u.%u (git tag: %s)\n", major, minor, git_tag);
	return 0;
}

