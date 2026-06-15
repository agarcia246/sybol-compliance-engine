# README #

Blockhaim manager is a connector to several blockcahin that simplifies the explotation of the DTL technologies

### How to run ###
**To run in production**
```
npm install
npm run start
```

**To run in dev**
```
npm install
npm run start-dev
```

### How to set up ###

The Vault needs to have a KV v2 engine enabled for the wallets path, by default, wallets named
All the configuration is in the config yaml file

# PERIMETER JWT SECURITY #
**API**[https://app.swaggerhub.com/apis/Grant_Thornton_ES/identityObjectsManager/1.0.0#](api-link)
## MOTIVATION ##

This is an example of how simple jwt server can be used to create a perimeter user security

## RUN ##

```shell
docker compose up
```

## DESIGN ##

The design is pegged to Nginx or any other proxy that you can set up in the perimeter to check Authorization header.

When any request reach the proxy, the proxy first check if it is authorized to call the endpoint, if it is, the request is passed fordward, in any other case, the request is rejected.

To validate the request, the proxy MUST call the /validate endpoint in authorization server

The authorization server has 2 responsibilities:

1. Manage the life cycle for JWT
2. Manage life cycle of derivated objects from JWT such like Credentials, PResentations and PResentation Request

```javascript
//SYBOLID
// const MODULE_NAME = 'config.bootstrap.js';

// ---------------------------------------------------------------------------
// IMPORTS
// ---------------------------------------------------------------------------
// ------NODE MODULES---------------------------------------------------------

// ------PRIVATE MODULES------------------------------------------------------

// ------FILE MODULES---------------------------------------------------------

// ---------------------------------------------------------------------------
// CONSTANTS
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// PRIVATE FUNCTIONS
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// PUBLIC FUNCTIONS
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// EXPORTS
// ---------------------------------------------------------------------------

LOG.traceHeader('info', MODULE_NAME, []);
```

### Manage the life cycle for JWT ###

This means:

- Creating a valid JWT when the user authenticates correctly
- Regenerating JWT tokens if near to expire
- Sign payload with account keys stored in valut
- verify tokens

### File schema ###

- All files include the layer extension
- Config must be done in /config.yaml or json extension
- Constants are in /src/helpers/constants

## TEST ##

Testing is built over JEST framework [https://jestjs.io/](https://jestjs.io/)
Test MUST be done under unit test rules, this means, that no dependancies should impact the test, only the tested module MUST be tested, if the file is a wrapper of a lib, lib MUST be included as a single exception to this.
The test are divided in 2 blocks under 1 big block, the big block is used to show the module name under test, and the 2 sub-subblocks define the postive and negative test cases (happy path vs errors)
The mocked modules need to return jest.fn, that will allow to spy and mock the dependancies.
