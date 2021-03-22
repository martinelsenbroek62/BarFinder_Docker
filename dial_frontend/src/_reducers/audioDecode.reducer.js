import {audioConstants} from '../_constants';

const INITIAL_STATE = {};

export function audioDecode(state = INITIAL_STATE, action) {
    switch (action.type) {
        case audioConstants.DECODE_SUBMITTING:
            return {
                submitting: true,
                processing: false
            };
        case audioConstants.DECODE_PROCESSING:
            return {
                submitting: false,
                processing: true,
                taskInfo: action.taskInfo
            };
        case audioConstants.DECODE_SUCCESS:
            return {
                submitting: false,
                processing: false,
                taskInfo: action.taskInfo
            };
        case audioConstants.DECODE_FAILURE:
            return {
                submitting: false,
                processing: false,
                error: action.error
            };
        default:
            return {
                submitting: false,
                processing: false
            };
    }
    ;
}

