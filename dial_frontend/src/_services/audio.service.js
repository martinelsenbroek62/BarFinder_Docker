import {apiUrl} from '../config';
import {authHeader} from '../_helpers';

export const audioService = {
    async decodeAudio({
                          files, engine, language, clusterMode,
                          numSpeakers, eng1Alpha, eng1Beta,
                          eng2SubsamplingFactor
                      }) {
        const taskList = [];
        const errors = [];
        for (const file of files) {
            const formData = new FormData();
            formData.append('file', file);
            for (const eng of engine) {
                formData.append('engine', eng);
            }
            formData.append('language', language);
            formData.append('cluster_mode', clusterMode);
            formData.append('num_speakers', numSpeakers);
            if (eng1Alpha) {
                formData.append('__eargs__xcel-1_alpha', eng1Alpha);
                formData.append('__eargs__xcel-3_alpha', eng1Alpha);
            }
            if (eng1Beta) {
                formData.append('__eargs__xcel-1_beta', eng1Beta);
                formData.append('__eargs__xcel-3_beta', eng1Beta);
            }
            if (eng2SubsamplingFactor) {
                formData.append(
                    '__eargs__xcel-2_subsampling_factor',
                    eng2SubsamplingFactor
                );
                formData.append(
                    '__eargs__xcel-4_subsampling_factor',
                    eng2SubsamplingFactor
                );
            }
            const resp = await fetch(`${apiUrl}/convert_audio`, {
                method: 'POST',
                cache: 'no-cache',
                headers: {
                    ...authHeader()
                },
                body: formData
            });

            if (resp.ok) {
                const taskInfo = await resp.json();
                for (const {task_id} of taskInfo) {
                    taskList.push(task_id);
                }
            }
            errors.push('Unknown API error');
        }
        const formData = new FormData();
        for (const taskId of taskList) {
            formData.append('task_ids', taskId);
        }
        const resp = await fetch(`${apiUrl}/task_subscription`, {
            method: 'POST',
            cache: 'no-cache',
            headers: {
                ...authHeader()
            },
            body: formData
        });

        if (resp.ok) {
            return await resp.json();
        }

        throw new Error('Unknown API error');
    },

    async fetchDecodeResult(bulkTaskId) {
        const resp = await fetch(`${apiUrl}/task_subscription/${bulkTaskId}`, {
            method: 'GET',
            cache: 'no-cache',
            headers: {
                ...authHeader()
            }
        });

        if (resp.ok) {
            return await resp.json();
        }

        throw new Error('Unknown API error');
    }
}
