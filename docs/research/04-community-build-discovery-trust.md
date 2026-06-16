# Finding 04: Build discovery is noisy; trust and anti-bait filtering are major pain points

## Research result

Players have too many build links and not enough confidence. The community build index itself warns that PoE2 build knowledge is weaker than PoE1 knowledge and that bait builds may slip through.

## Evidence

The r/pathofexile2builds 0.5 league starter index is a large community resource, but it explicitly says it is under construction, asks users to post builds from Reddit/YouTube/Mobalytics/Maxroll/forum sources, and warns readers to do due diligence. It also says the author's PoE2 knowledge is worse than PoE1 knowledge and that bait builds may sneak in.

The subreddit homepage also shows:

- build requests
- build review posts
- creator-specific guide links
- questions about whether guides are trustworthy
- rules requiring build posts to include a description

## User pain

A user searching "best PoE2 beginner build" is really asking:

- Is this build proven or bait?
- Is it budget viable?
- Does it work for campaign, maps, pinnacle bosses, or only showcase gear?
- Has it been updated after 0.5.2?
- Is there a `.build` file?

## Product implication

The site needs a trust rubric for each build:

- source type: official/example/community/creator/self-tested
- patch verified date
- budget floor
- gear dependency score
- complexity score
- controller friendliness
- hardcore/SSF/trade viability
- known failure mode

## Site content format

Instead of "Best Builds" only, publish "Build Cards":

```yaml
build_name: Example
patch: 0.5.2
source: creator/reddit/self-tested
budget: low/medium/high
gear_dependency: low/medium/high
complexity: low/medium/high
import_file: yes/no
proof: video/log/screenshots/community consensus
risk: stale/nerfed/expensive/boss-only
```

## Sources

- Reddit 0.5 league starter build index: https://www.reddit.com/r/pathofexile2builds/comments/1tny1to/05_return_of_the_ancients_league_starter_build/
- r/pathofexile2builds homepage/resources/rules: https://www.reddit.com/r/pathofexile2builds/
- Reddit beginner/budget build demand: https://www.reddit.com/r/pathofexile2builds/comments/1tqjr6g/whats_a_good_beginnerbudget_friendly_build_for_05/
