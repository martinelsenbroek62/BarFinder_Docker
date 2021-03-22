import {usageStatConstants} from '../_constants';
import {usageStatService} from '../_services';


export const usageStatActions = {
    fetch() {

        return async dispatch => {

            try {
                const usageStatInfo = await usageStatService.fetch();
                dispatch({
                    type: usageStatConstants.FETCH_SUCCESS,
                    usageStatInfo
                });
            } catch (error) {
                dispatch({
                    type: usageStatConstants.FETCH_FAILURE,
                    error: error.message
                });
            }

        };

    }

}
