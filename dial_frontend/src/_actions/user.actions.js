import {userService} from '../_services';
import {userConstants} from '../_constants';
import {history} from '../_helpers';


export const userActions = {
    signin(email, password) {

        return async dispatch => {
            dispatch({
                type: userConstants.SIGNIN_REQUEST,
                tokenInfo: {email}
            });

            try {
                const tokenInfo = await userService.signin(email, password);
                dispatch({
                    type: userConstants.SIGNIN_SUCCESS,
                    tokenInfo
                });
                history.push('/');
            } catch (error) {
                dispatch({
                    type: userConstants.SIGNIN_FAILURE,
                    error: error.message
                });
            }

        };

    },

    signout() {
        return dispatch => {
            userService.signout();
            dispatch({type: 'USER_SIGNOUT'});
            history.push('/');
        };
    }

}
