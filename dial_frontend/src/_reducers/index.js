import {combineReducers} from 'redux';
import {auth} from './auth.reducer';
import {audioDecode} from './audioDecode.reducer';
import {usageStat} from './usageStat.reducer';

const rootReducer = combineReducers({
    auth, audioDecode, usageStat
});

export default rootReducer;
