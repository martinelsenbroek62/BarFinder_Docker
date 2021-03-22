import {apiUrl} from '../config';
import {authHeader} from '../_helpers';

export const usageStatService = {

    async fetch() {
        const resp = await fetch(`${apiUrl}/usage_stat`, {
            method: 'POST',
            cache: 'no-cache',
            headers: {
                ...authHeader()
            }
        })
        if (resp.ok) {
            return await resp.json();
        }
        const {message} = await resp.json();
        throw new Error(message);
    }

}
