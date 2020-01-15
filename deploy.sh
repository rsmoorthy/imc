#!/bin/bash

$(cd dist/main; bash ../../strip.sh)
$(cd dist/main; ln main main_gui)
$(cd dist/main; ln main menu_osd)
cp config.json dist/main
cp -a resources dist/main
$(cd dist/main; tar zcf /tmp/imc.tgz .)



