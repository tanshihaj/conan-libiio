conan remote add tanshihaj-main https://api.bintray.com/conan/tanshihaj/main
conan user -p $BINTRAY_API_KEY -r tanshihaj-main tanshihaj
conan upload libiio -r tanshihaj-main --all --confirm --force