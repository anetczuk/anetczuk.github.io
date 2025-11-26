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


## data generation

Information about repos can be grabbed by script `./src/gen/read_github.py`.
To generate descriptions of repositories execute `./src/gen/generate_description.py`. 

Generation of fav icons is done by script `./src/logo/generate_icons.sh`.

To refresh information about repositories make following steps:
1. run script `src/gen/read_github.py`
2. open dumped file (`tmp/github_repos.csv`) and update information in repos description file (`src/gen/repos_description.csv`)
3. generate static pages using script `src/gen/generate_description.py`


## theme

Site uses [Holo Alfa](http://stijnvc.github.io/holo-alfa) Jekyll theme crafted by [Stijn](http://stijnvc.github.io/holo-alfa). Theme is published on [MIT license](http://opensource.org/licenses/MIT).


## references 

- GitHub Pages https://pages.github.com/
