import {userService} from '../_services';

export function authHeader() {
    const tokenInfo = userService.getStoredToken();
    if (tokenInfo) {
        return {
            Authorization: `Bearer ${tokenInfo.access_token}`
        };
    } else {
        return {};
    }
}
