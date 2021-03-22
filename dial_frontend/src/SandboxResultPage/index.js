import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';

import Loader from 'react-loader';
import {Row, Col, Button} from 'react-bootstrap';

import {audioActions} from '../_actions';
import {
    makeDownload,
    makeCSVDownload,
    makeMultipleCSVDownload,
    makeZIPDownload,
    makeJSONDownload
} from '../_helpers';


class SandboxResultPage extends React.Component {

    static propTypes = {
        taskInfo: PropTypes.shape({
            status: PropTypes.string.isRequired,
            completed_count: PropTypes.number,
            total_count: PropTypes.number,
            task_results: PropTypes.object
        }),
        fetchDecodeResult: PropTypes.func.isRequired,
        location: PropTypes.shape({
            search: PropTypes.string.isRequired
        }).isRequired
    }

    constructor() {
        super(...arguments);

        const {fetchDecodeResult, location} = this.props;
        const query = new URLSearchParams(location.search);

        fetchDecodeResult(query.get('bulk_task_id'));

        this.handleCSVDownload = this.handleCSVDownload.bind(this);
        this.handleWordLevelCSVDownload = this.handleWordLevelCSVDownload.bind(this);
        this.handleTXTDownload = this.handleTXTDownload.bind(this);
        this.handleJSONDownload = this.handleJSONDownload.bind(this);
    }


    handleTXTDownload() {
        const {taskInfo: {bulk_task_id, task_results}} = this.props;
        const files = [];
        for (const {status, task_result} of task_results) {
            if (status !== 'SUCCESS') {
                // skip non-success tasks
                continue;
            }
            const {filename, engine, language, created_at} = task_result;
            let nodot_filename = filename.replace(/\./g, '_');
            const fileName = `${nodot_filename}__${engine}_${language}_${created_at}.txt`;
            const rows = [];
            for (const row of task_result.transcripts) {
                rows.push(row.content);
            }
            files.push({fileName, mediaType: 'text/plain', data: rows.join('\n')});
        }
        if (files.length !== 1) {
            makeZIPDownload(
                `bulk_result_${bulk_task_id}.zip`, files
            );
        } else {
            const [{fileName, mediaType, data}] = files;
            makeDownload(fileName, mediaType, data);
        }
    }


    handleCSVDownload() {
        const {taskInfo: {bulk_task_id, task_results}} = this.props;
        const files = [];
        for (const {status, task_result} of task_results) {
            if (status !== 'SUCCESS') {
                // skip non-success tasks
                continue;
            }
            const {filename, engine, language, created_at} = task_result;
            let nodot_filename = filename.replace(/\./g, '_');
            const fileName = `${nodot_filename}__${engine}_${language}_${created_at}.csv`;
            const rows = [
                ['speaker', 'startTime', 'duration', 'sentence', 'avgConfidence']
            ];
            for (const row of task_result.transcripts) {
                const words = row.word_chunks;
                const sentence = row.content;
                const avgconf = (
                    words.reduce((acc, w) => acc + w.confidence, .0) /
                    words.length);
                rows.push([
                    row.speaker,
                    row.stime,
                    row.duration,
                    sentence,
                    avgconf
                ]);
            }
            files.push({fileName, rows});
        }
        if (files.length !== 1) {
            makeMultipleCSVDownload(
                `bulk_result_${bulk_task_id}.zip`, files
            );
        } else {
            const [{fileName, rows}] = files;
            makeCSVDownload(fileName, rows);
        }
    }

    handleWordLevelCSVDownload() {
        const {taskInfo: {bulk_task_id, task_results}} = this.props;
        const files = [];
        for (const {status, task_result} of task_results) {
            if (status !== 'SUCCESS') {
                // skip non-success tasks
                continue;
            }
            const {filename, engine, language, created_at} = task_result;
            let noext_filename = filename.split('.');
            noext_filename.splice(-1);
            const fileName = `${noext_filename}__by-word_${engine}_${language}_${created_at}.csv`;
            const rows = [
                ['speaker', 'startTime', 'duration', 'word', 'confidence']
            ];
            for (const row of task_result.transcripts) {
                const words = row.word_chunks;
                for (const word of words) {
                    rows.push([
                        row.speaker,
                        word.stime,
                        word.duration,
                        word.content,
                        word.confidence
                    ])
                }
            }
            files.push({fileName, rows});
        }
        if (files.length !== 1) {
            makeMultipleCSVDownload(
                `bulk_result_by-word_${bulk_task_id}.zip`, files
            );
        } else {
            const [{fileName, rows}] = files;
            makeCSVDownload(fileName, rows);
        }
    }

    handleJSONDownload() {
        const {taskInfo: {bulk_task_id, task_results}} = this.props;
        makeJSONDownload(`bulk_result_${bulk_task_id}.json`, task_results);
    }

    get taskStatus() {
        const {taskInfo} = this.props;
        if (taskInfo) {
            return taskInfo.status;
        }
        return null;
    }

    get taskId() {
        const {taskInfo} = this.props;
        if (taskInfo) {
            return taskInfo.bulk_task_id;
        }
        return null;
    }

    get completedCount() {
        const {taskInfo} = this.props;
        if (taskInfo) {
            return taskInfo.completed_count;
        }
        return null;
    }

    get totalCount() {
        const {taskInfo} = this.props;
        if (taskInfo) {
            return taskInfo.total_count;
        }
        return null;
    }

    render() {
        const {taskStatus, taskId, completedCount, totalCount} = this;
        return
    <
        Row >
        < Col >
        < h1 > AudioDecoder
        Sandbox
        Result < /h1>
        < p > Task
        ID: {
            taskId
        }
    <
        /p>
        {
            taskStatus === 'PENDING' && totalCount ?
        <
            p > Completed
        :
            {
                completedCount
            }
            /{totalCount}</
            p >
        :
            null
        }
    <
        Loader
        loaded = {taskStatus === 'SUCCESS'
    }>
    <
        p >
        < Button
        onClick = {this.handleCSVDownload}
        variant = "primary" >
            Download
        CSV(Sentence
        Level
    )
    <
        /Button>
        < Button
        onClick = {this.handleWordLevelCSVDownload}
        variant = "primary" >
            Download
        CSV(Word
        Level
    )
    <
        /Button>
        < Button
        onClick = {this.handleTXTDownload}
        variant = "default" >
            Download
        TXT
        < /Button>
        < Button
        onClick = {this.handleJSONDownload}
        variant = "default" >
            Download
        JSON
        < /Button>
        < /p>
        < /Loader>
        < /Col>
        < /Row>
    }

}


function mapState(state) {
    const {taskInfo} = state.audioDecode;
    return {taskInfo};
}

const actionCreators = {
    fetchDecodeResult: audioActions.fetchDecodeResult
}

export default connect(mapState, actionCreators)(SandboxResultPage);
