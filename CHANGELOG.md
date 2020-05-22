# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

## [1.0.0](https://github.com/jmartinezhern/pointing_poker/compare/v1.1.0...v1.0.0) (2020-05-22)

## 1.1.0 (2020-05-22)


### Features

* add missing lambda data sources and resolvers ([d3a3184](https://github.com/jmartinezhern/pointing_poker/commit/d3a3184e3ad2a036068833f195e1dfbcb1bd8da1))
* clean up handlers and move to AWS CDK ([4e33154](https://github.com/jmartinezhern/pointing_poker/commit/4e331546f86fd123f1729b744f115cf348c66568))
* implement join_session, session handlers and improve design ([2646080](https://github.com/jmartinezhern/pointing_poker/commit/2646080673f7a6be9af6ab74bdfec5fb0573269b))
* implement repository code for the rest of the mutations ([b9790a5](https://github.com/jmartinezhern/pointing_poker/commit/b9790a58facfa8e8b3ef54a96455077fe394e21b))
* introduce ttl/expirations ([81ae9e2](https://github.com/jmartinezhern/pointing_poker/commit/81ae9e24e65cb71d047a16a10e4a64f3afa4ecf6))
* track if a session is in a closed state ([aa82c53](https://github.com/jmartinezhern/pointing_poker/commit/aa82c5369f4e584216075930606853a06e6d1dd3))
* use shorter session IDs ([6ae9a9c](https://github.com/jmartinezhern/pointing_poker/commit/6ae9a9c8f6e2da71d717694c654b456367ee31b8))


### Bug Fixes

* add missing controllers and data sources ([b50eb03](https://github.com/jmartinezhern/pointing_poker/commit/b50eb034bf77d45f8423496627e2adfc3e4ecc91))
* connect missing controllers ([f548253](https://github.com/jmartinezhern/pointing_poker/commit/f54825390ba5b67aca5a8938882f59d3cc5882ea))
* correct issues with GraphQL schema ([a74d0fc](https://github.com/jmartinezhern/pointing_poker/commit/a74d0fcce2f32b5201609cff3064f2afe230f671))
* do not default record expiration ([6c07efa](https://github.com/jmartinezhern/pointing_poker/commit/6c07efaff67df7098b8e8ad1bec83a258d55bb98))
* fields should be properly non-null or null ([1880e4a](https://github.com/jmartinezhern/pointing_poker/commit/1880e4aec3c578c1a3cfad371903d88d4972c400))
* miss calculation in expiration date ([b6c7104](https://github.com/jmartinezhern/pointing_poker/commit/b6c710467ec3881a7dd02dcc5bc98c814c560ff9))
* normalize session and corresponding record expiration ([1f5562d](https://github.com/jmartinezhern/pointing_poker/commit/1f5562d69e0c18e1ce38d4024b318da3f7b3bcf0))
* order of operations error ([ef9f914](https://github.com/jmartinezhern/pointing_poker/commit/ef9f9141d2adab4a21169df7ab818360cf9469a1))
* pass correct record expiration on session create ([898085c](https://github.com/jmartinezhern/pointing_poker/commit/898085cc39adbeb3fc5b3f132f8b2866b65319bd))
* pass participant id from the client ([1830555](https://github.com/jmartinezhern/pointing_poker/commit/18305556b136970f4a506b9581c2f0ca83d8c882))
* properly represent voting state of participants ([42267f9](https://github.com/jmartinezhern/pointing_poker/commit/42267f91c9406d5c44a0fbb9ddff5b423245662e))
* review issue field should be required ([5fbe361](https://github.com/jmartinezhern/pointing_poker/commit/5fbe36103e16c775d0258a0f20a654376b90817d))
