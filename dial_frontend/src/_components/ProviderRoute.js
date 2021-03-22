import React from 'react';
import {Route, Redirect} from 'react-router-dom';

import {userService} from '../_services';

export const PrivateRoute = ({component: Component, ...rest}) => (
    < Route
{...
    rest
}
render = {props
=>
(
    userService.getStoredToken()
        ? (Component ? < Component {...props}
/> : null)
: <
Redirect
to = {
{
    pathname: '/signin', state
:
    {
        from: props.location
    }
}
}
/>
)
}
/>
)
