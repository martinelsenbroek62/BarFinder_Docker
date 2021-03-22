import sleep from 'sleep-promise';

import {audioService} from '../_services';
import {audioConstants} from '../_constants';
import {history} from '../_helpers';


export const audioActions = {

    decodeAudio({
                    files, engine, language, clusterMode,
                    numSpeakers, eng1Alpha, eng1Beta,
                    eng2SubsamplingFactor
                }) {

        return async dispatch => {
            dispatch({type: audioConstants.DECODE_SUBMITTING});

            try {
                const taskInfo = await audioService.decodeAudio({
                    files, engine, language, clusterMode,
                    numSpeakers, eng1Alpha, eng1Beta,
                    eng2SubsamplingFactor
                });
                dispatch({
                    type: audioConstants.DECODE_PROCESSING,
                    taskInfo
                });
                const {bulk_task_id} = taskInfo;
                history.push(
                    `/sandbox/result?bulk_task_id=${encodeURIComponent(bulk_task_id)}`
                );
            } catch (error) {
                dispatch({
                    type: audioConstants.DECODE_FAILURE,
                    error: error.message
                });
            }

        };

    },

    fetchDecodeResult(bulkTaskId) {

        return async dispatch => {

            let sleepInterval = 10000;
            let taskInfo;
            let taskStatus;

            do {
                try {
                    taskInfo = await audioService.fetchDecodeResult(bulkTaskId);
                    taskStatus = taskInfo.status;
                    if (taskStatus === 'SUCCESS') {
                        dispatch({
                            type: audioConstants.DECODE_SUCCESS,
                            taskInfo
                        });
                    } else if (taskStatus === 'FAILURE') {
                        dispatch({
                            type: audioConstants.DECODE_FAILURE,
                            taskInfo
                        });
                    } else if (taskStatus === 'PENDING') {
                        dispatch({
                            type: audioConstants.DECODE_PROCESSING,
                            taskInfo
                        });
                        await sleep(sleepInterval);
                    } else {
                        dispatch({
                            type: audioConstants.DECODE_FAILURE,
                            taskInfo
                        });
                    }
                } catch (error) {
                    await sleep(sleepInterval);
                }
            } while (taskStatus === 'PENDING');

        }

    }

};
