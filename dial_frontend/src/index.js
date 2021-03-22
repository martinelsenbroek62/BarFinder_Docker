import React from 'react';
import ReactDOM from 'react-dom';
import {Provider} from 'react-redux';

import 'normalize.css';
import 'bootstrap/scss/bootstrap.scss';
import 'mdbootstrap/scss/mdb.scss';
import App from './App';
import {store} from './_helpers';
import * as serviceWorker from './serviceWorker';

ReactDOM.render(
< Provider
store = {store} >
    < App / >
    < /Provider>,
document.getElementById('root')
)
;

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
