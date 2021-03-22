import {userService} from '../_services';
import {userConstants} from '../_constants';

const INITIAL_STATE = {};

export function auth(state = INITIAL_STATE, action) {
    switch (action.type) {
        case userConstants.SIGNIN_REQUEST:
            return {
                signingIn: true,
                signedIn: false,
                tokenInfo: action.tokenInfo
            };
        case userConstants.SIGNIN_SUCCESS:
            return {
                signingIn: false,
                signedIn: true,
                tokenInfo: action.tokenInfo
            };
        case userConstants.SIGNIN_FAILURE:
            return {
                signingIn: false,
                signedIn: false,
                error: action.error
            };
        case userConstants.SIGNOUT:
            return {
                signingIn: false,
                signedIn: false
            };
        default:
            if (state === INITIAL_STATE) {
                const tokenInfo = userService.getStoredToken();
                state = tokenInfo ? {
                    signingIn: false,
                    signedIn: true,
                    tokenInfo
                } : {
                    signingIn: false,
                    signedIn: false
                };
            }
            return state;
    }
    ;
}

