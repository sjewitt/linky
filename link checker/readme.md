#Linky
Spidering and link analysis framework


##Summary
A simple Python3 spidering utility that records unique hrefs found on each page spidered. The original use-case was to search for fully qualified links that were not ssl-enabled, but the core spider simply collects all links found.

The unique feature of this spider is the abiliy to use an array of root domains to analyse - designed originally to account for sub-domains. The collected list of links on each html page includes only those in the list of domains.

Currently, `<link>`, `<a>` and `<img>` tags are analysed, but the plan is to make this configurable.

##TODO
 - properly parameterise startup
 - utilise phantomJS or similar to allow analysis of bynamic pages
     - account for URL parameters
 - properly document!  