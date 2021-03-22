import {createStore, applyMiddleware} from 'redux';
import thunkMiddleware from 'redux-thunk';
import promiseMiddleware from 'redux-promise';
import {createLogger} from 'redux-logger';
import rootReducer from '../_reducers';

const loggerMiddleware = createLogger();

export const store = createStore(
    rootReducer,
    applyMiddleware(
        thunkMiddleware,
        promiseMiddleware,
        loggerMiddleware
    )
);
