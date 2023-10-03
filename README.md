# anetczuk.github.io

Account site hosted by GitHub Pages. Webpage is available at https://anetczuk.github.io/


## requirements

- `pandas` (`pip3 install pandas`)
- `requests_file` (`pip3 install requests_file`)
- `cloc` (`sudo apt install cloc`)
- `bundler` (`sudo apt install bundler`)


## previewing locally

To preview site locally run script `./tools/startlocal.sh`. Local build will be ready at `http://127.0.0.1:4000/` Before first run it is required to
initialize build by `./tools/initbundle.sh`.


## generating data

To generate descriptions of repositories execute `./src/gen/repos_generator.sh`. 
Moreover information about repos can be grabbed by script `./src/gen/github_reader.sh`.

Generation of fav icons is done by script `./src/logo/generate_icons.sh`.

To refresh information about repositories make following steps:
1. run script `github_reader.sh`
2. open dumped file and update information in repos description file (`repos_description.csv`)
3. generate static pages using script `repos_generator.sh`


## theme

Site uses [Holo Alfa](http://stijnvc.github.io/holo-alfa) Jekyll theme crafted by [Stijn](http://stijnvc.github.io/holo-alfa). Theme is published on [MIT license](http://opensource.org/licenses/MIT).


## references 

- GitHub Pages https://pages.github.com/
