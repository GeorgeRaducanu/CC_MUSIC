# Changelog

# CC_MUSIC

## Arpășanu Emilia Oana && Răducanu George-Cristian - 341C1

All changes to this project CC_MUSIC will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

For simplicity we will use abreviations to mark the author of each change:
-  Arpășanu Emilia Oana -> ***EA***
-  Răducanu George-Cristian -> ***GR***


## [1.2.0] - 03.05.2024

### Added

- Added mean rating information for song (***GR***)
- Added insert song and author from user interface (***GR*** && ***EA***)

## [1.1.0] - 02.05.2024

### Added

- Added rating in database and business logic (***EA***)
- Created a page for each song for information and link redirection (***EA***)

## [1.0.0] - 19.04.2024

### Added

- Added folder content template (***EA***)
- Added add-song-to-folder and create-folder templates and routes (***GR*** & ***EA***)
- Added add-song-to-folder and create-folder operations in IO_service (***EA***)

## [0.1.2] - 18.04.2024

### Added

- Added portainer (***GR***)
- Added gitlab ci/cd yml (***GR***)

## [0.1.1] - 17.04.2024

### Added

- Added app routes and queries in IO_service for retreival fo information (***GR*** & ***EA***)
- Added in database schema to store folders for song organization. (***EA***)
- Retrieved folder and songs data from io service (***EA***)

## [0.1.0] - 14.04.2024

### Added

- Added validation function for jwt tokens (***EA*** & ***GR***)

### Changed

- Remove public kong ip address in docker compose and modified code to make it work without it (***GR***)

## [0.0.4] - 12.04.2025

### Added

- Added adminer, prometheus and grafana for management in dockerfile compose and also in code (***GR***)
- Finalized in business logic the main route of the server (***GR***)
- Finalized access credentials (***EA***)

### Changed

- Modified flow in docker compose for efficiency and separation (network and volume separation) (***GR***)

## [0.0.3] - 11.04.2025

### Added

- Added adminer, prometheus and grafana for management in dockerfile compose and also in code (***GR***)
- Added code for login and authentification (***EA***)

### Changed

- Changed file name of python file in microservice to match name convention(***GR***)

## [0.0.2] - 11.04.2025

### Added

- Added docker compose file for container management (***GR***)
- Added python microservices in network (***GR***)
- Added database schema - first version and correspondind dockerfile (***GR***)


## [0.0.1] - 03.04.2025

### Added
- Added Dockerfile in each repository (***GR***)
- Added requirements files for python microservices and first skeleton for them (***GR***)

## [0.0.0] -  02.04.2025

### Added

- Created repositories for project (***GR***)
- Added README for each microservices and .gitignore (***GR***)