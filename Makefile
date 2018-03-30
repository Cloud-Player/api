install:
	@python3.6 -m venv --upgrade --copies .
	bin/pip3.6 install -e .[test,doc]

sphinx:
	bin/sphinx-build -N -b singlehtml source build

shins:
	@npm i -g shins widdershins
	@mkdir -p ./shins
	widdershins -e widdershins.json --omitBody --resolve spec/restapi.yml source/restapi.html.md
	shins --minify --inline --logo source/images/logo.png -o shins/restapi.html source/restapi.html.md
	widdershins -e widdershins.json --omitBody --resolve spec/asyncapi.yml source/asyncapi.html.md
	shins --minify --inline --logo source/images/logo.png -o shins/asyncapi.html source/asyncapi.html.md
	@grep -v "X509" shins/asyncapi.html > temp && mv temp shins/asyncapi.html

.DEFAULT: install sphinx shins
.PHONY: install sphinx shins
