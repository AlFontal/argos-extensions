# Argos Extensions

Just a compilation of some GNOME Shell extensions which add collapsible indicators in the Gnome top bar
that I have made for my personal machine and that might be useful to adapt for someone else.

These have been built using the nice API provided by [p-e-w's Argos](https://github.com/p-e-w/argos)
project, which provides an easy-to-use API (via Python or Bash scripts) to avoid the need for
direct interaction with the ever-changing JavaScript API of GNOME. 

The `pyproject.toml` file specifies the Python dependencies of the project. Each different extension might have different
needs, but since they were basically completely overlapping, I just generated a single environment. In case you don't want
to use `poetry`, the basic dependencies to be able to run the extensions are: 

+ `pandas`
+ `requests`
+ `plotnine`

## Live preview

### Github and Gitlab repos indicator

This extension accesses Gitlab and Github's APIs in an authenticated manner (you need to generate some access tokens in order to
be able to access your private repos), and provides an easy collapsible indicator that fetches your recently active repos in both
sites and gives quick links to access the main repo, their issues, or the Pages/Homepage of the project.

https://user-images.githubusercontent.com/10958332/167110649-aa58a3f4-110d-4ac2-9526-dbeb089d037b.mp4


### Nightscout glucose indicator

This extension depends on [Nightscout](https://nightscout.github.io/), which acts as a database and dashboard of continuous glucose monitoring (CGM)
readings and which has a queryable API.

In this indicator I fetch the values for the last 4 hours, display the last value with an arrow to indicate the current trend of glucose and when
hovering it displays a figure with the evolution of the values for the last 4 hours:

https://user-images.githubusercontent.com/10958332/167110435-ad247229-151b-43a7-b279-c9c30cf63d75.mp4
