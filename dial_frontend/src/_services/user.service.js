import {apiUrl} from '../config';

const TOKEN_KEY = 'accessToken';

export const userService = {

    async signin(email, password) {
        const formData = new FormData();
        formData.append('email', email);
        formData.append('password', password);

        const resp = await fetch(`${apiUrl}/access_token`, {
            method: 'POST',
            cache: 'no-cache',
            body: formData
        });
        if (resp.ok) {
            const tokenInfo = await resp.json();
            localStorage.setItem(TOKEN_KEY, JSON.stringify(tokenInfo));
            return tokenInfo;
        }
        const {message} = await resp.json();
        throw new Error(message);
    },

    getStoredToken() {
        const data = localStorage.getItem(TOKEN_KEY);
        if (!data) {
            return null;
        }
        const tokenInfo = JSON.parse(data);
        const expTime = new Date(tokenInfo.expiration);
        const now = new Date();
        if (now.getTime() > expTime.getTime() - 300000) {
            // expires 5 minutes earlier
            localStorage.removeItem(TOKEN_KEY);
            return null;
        }
        return tokenInfo;
    },

    signout() {
        localStorage.removeItem(TOKEN_KEY);
    }

}
