import {usageStatConstants} from '../_constants';

const INITIAL_STATE = {};

export function usageStat(state = INITIAL_STATE, action) {
    switch (action.type) {
        case usageStatConstants.FETCH_SUCCESS:
            return {
                usageStatFetched: true,
                usageStatInfo: action.usageStatInfo
            };
        case usageStatConstants.FETCH_FAILURE:
            return {
                usageStatFetched: false,
                error: action.error
            };
        default:
            return {
                usageStatFetched: false
            };
    }
    ;
}

