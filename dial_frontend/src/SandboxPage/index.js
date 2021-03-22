import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';

import * as Yup from 'yup';
import {Formik} from 'formik';
import classNames from 'classnames';
import Dropzone from "react-dropzone";
import {Row, Col, Form, Button} from 'react-bootstrap';

import {audioActions} from '../_actions';

import style from './style.module.scss';

const ENGINES = [
    {value: 'xcel-3', label: 'Engine Type 1 (CPU)'},
    {value: 'xcel-1', label: 'Engine Type 1 (GPU-Accelerated)'},
    {value: 'xcel-4', label: 'Engine Type 2 (CPU)'},
    {value: 'xcel-2', label: 'Engine Type 2 (GPU-Accelerated)'},
    {value: 'xcel-6', label: 'Engine Type 3 (CPU)'},
    {value: 'xcel-5', label: 'Engine Type 3 (GPU-Accelerated)'},
];

const LANGUAGES = [
    {value: 'en', label: 'English'},
    {value: 'en2', label: 'English v2'},
    {value: 'en-us', label: 'English (US)'},
    {value: 'en-uk', label: 'English (UK)'},
    {value: 'zh', label: 'Chinese Mandarin'},
    {value: 'ja', label: 'Japanese'}
];

const LANGUAGE_ENGINES = {
    'en': ['xcel-1', 'xcel-2', 'xcel-3', 'xcel-4'],
    'en2': ['xcel-2', 'xcel-4'],
    'en-us': ['xcel-2', 'xcel-4'],
    'en-uk': ['xcel-2', 'xcel-4'],
    'zh': ['xcel-1', 'xcel-2', 'xcel-3', 'xcel-4'],
    'ja': ['xcel-5', 'xcel-6'],
};

const CLUSTER_MODES = [
    {value: '0', label: 'Auto-detect number of speakers'},
    {value: '1', label: 'Designate number of speakers'}
];

const MAX_FILE_SIZE = 500 * 1024 * 1024;
const SUPPORTED_FORMATS = ['audio/wav', 'audio/mp3', 'audio/flac'];

const ENG2_SUBSAMPLING_FACTORS = ['1', '2', '3', '4', '5'];

function getValues(arr) {
    return arr.map(({value}) => value);
}

const schema = Yup.object().shape({
    files: (
        Yup.array().of(
            Yup.mixed()
                .test(
                    'fileRequired',
                    'File is required',
                    val => val instanceof File
                )
                .test(
                    'fileSize',
                    'File Size is too large (max size: ' +
                    `${(MAX_FILE_SIZE / 1048576).toFixed(0)}MB)`,
                    val => val.size < MAX_FILE_SIZE)
                .test(
                    'fileType', 'Unsupported File Format',
                    val => SUPPORTED_FORMATS.includes(val.type))
                .required()
        )
    ).required(),
    language: Yup.mixed().oneOf(getValues(LANGUAGES)).required(),
    engine: Yup.array().of(
        Yup.mixed().oneOf(getValues(ENGINES)).required()
    ).required(),
    clusterMode: Yup.mixed().oneOf(getValues(CLUSTER_MODES)).required(),
    numSpeakers: Yup.number().min(1).required(),
    eng1Alpha: (
        Yup.string()
            .matches(
                /^([0-4](\.\d+)?|5(\.0+)?)$/,
                {message: 'Not a valid floating number between 0.00-5.00.'}
            ).required()
    ),
    eng1Beta: (
        Yup.string()
            .matches(
                /^([0-4](\.\d+)?|5(\.0+)?)$/,
                {message: 'Not a valid floating number between 0.00-5.00.'}
            ).required()
    ),
    eng2SubsamplingFactor: Yup.mixed().oneOf(ENG2_SUBSAMPLING_FACTORS).required()

}).required();

const initialValues = {
    files: [],
    engine: [],
    language: 'en',
    clusterMode: '0',
    numSpeakers: 2,
    eng1Alpha: '0.75',
    eng1Beta: '1.85',
    eng2SubsamplingFactor: '3'
};

class SandboxPage extends React.Component {

    static propTypes = {
        submitting: PropTypes.bool.isRequired,
        error: PropTypes.bool,
        decodeAudio: PropTypes.func.isRequired
    }

    constructor() {
        super(...arguments);

        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleSubmit({
                     files, engine, language, clusterMode,
                     numSpeakers, eng1Alpha, eng1Beta,
                     eng2SubsamplingFactor
                 }) {
        this.props.decodeAudio({
            files, engine, language, clusterMode,
            numSpeakers, eng1Alpha, eng1Beta,
            eng2SubsamplingFactor
        });
    }

    render() {
        const {submitting} = this.props;
        return
    <
        Row >
        < Col
        sm = {8}
        xs = {12} >
            < h1 > AudioDecoder
        Sandbox < /h1>
        < Formik
        validationSchema = {schema}
        onSubmit = {this.handleSubmit}
        initialValues = {initialValues} >
            {(({
                   handleSubmit,
                   handleChange,
                   setFieldValue,
                   values,
                   isValid,
                   errors
               }) => (
                < Form
        noValidate
        onSubmit = {handleSubmit} >
            < Form.Group
        controlId = "formSandboxLanguage" >
        < Form.Label > Language < /Form.Label>
        < Form.Control
        as = "select"
        name = "language"
        value = {values.language}
        onChange = {event
    =>
        {
            handleChange(event);
            setFieldValue('engine', []);
        }
    }
        isInvalid = {
        !!errors.language
    }>
        {
            LANGUAGES.map(({value, label}, idx) => (
                < option
            key = {idx}
            name = "language"
            value = {value} > {label} < /option>
        ))
        }
    <
        /Form.Control>
        < Form.Control.Feedback
        type = "invalid" >
            {errors.language}
            < /Form.Control.Feedback>
            < /Form.Group>
        {
            !!values.language ?
        <
            Form.Group
            controlId = "formSandboxEngine" >
                < Form.Label > Engines < /Form.Label>
            {
                ENGINES.map(({value, label}, idx) => {
                    if (LANGUAGE_ENGINES[values.language].indexOf(value) < 0) {
                        return null;
                    }
                    return
                <
                    Form.Check
                    key = {idx}
                    id = {`engine-${value}`
                }
                    type = "checkbox"
                    data - value = {value}
                    checked = {values.engine.includes(value)}
                    onChange = {event
                =>
                    {
                        let {engine} = values;
                        const value = event.currentTarget.dataset.value;
                        const add = event.currentTarget.checked;
                        if (add && !engine.includes(value)) {
                            engine = [...engine, value];
                        } else if (!add && engine.includes(value)) {
                            engine = [...engine];
                            engine.splice(engine.indexOf(value), 1);
                        }
                        setFieldValue('engine', engine);
                    }
                }
                    isInvalid = {
                    !!errors.engine
                }
                    label = {label}
                    />
                })
            }
        <
            Form.Control.Feedback
            type = "invalid" >
                {errors.engine}
                < /Form.Control.Feedback>
                < /Form.Group> : null}
            {
                values.engine.includes('xcel-1') ||
                values.engine.includes('xcel-3') ?
            <>
            <
                Form.Group
                controlId = "formSandboxEng1Alpha" >
                    < Form.Label >
                    Engine
                1
                Alpha
                < /Form.Label>
                < Form.Control
                as = "input"
                type = "number"
                step = "0.05"
                min = "0.00"
                max = "5.00"
                name = "eng1Alpha"
                value = {values.eng1Alpha}
                onChange = {handleChange}
                isInvalid = {
                !!errors.eng1Alpha
            }
                />
                < Form.Control.Feedback
                type = "invalid" >
                    {errors.eng1Alpha}
                    < /Form.Control.Feedback>
                    < /Form.Group>
                    < Form.Group
                controlId = "formSandboxEng1Beta" >
                    < Form.Label >
                    Engine
                1
                Beta
                < /Form.Label>
                < Form.Control
                as = "input"
                type = "number"
                step = "0.05"
                min = "0.00"
                max = "5.00"
                name = "eng1Beta"
                value = {values.eng1Beta}
                onChange = {handleChange}
                isInvalid = {
                !!errors.eng1Beta
            }
                />
                < Form.Control.Feedback
                type = "invalid" >
                    {errors.eng1Beta}
                    < /Form.Control.Feedback>
                    < /Form.Group>
                    < /> : null}
                {
                    values.engine.includes('xcel-2') ||
                    values.engine.includes('xcel-4') ?
                <
                    Form.Group
                    controlId = "formSandboxEng2SubsamplingFactor" >
                        < Form.Label >
                        Engine
                    2
                    Subsampling
                    Factor
                    < /Form.Label>
                    < Form.Control
                    as = "select"
                    name = "eng2SubsamplingFactor"
                    value = {values.eng2SubsamplingFactor}
                    onChange = {handleChange}
                    isInvalid = {
                    !!errors.eng2SubsamplingFactor
                }>
                    {
                        ENG2_SUBSAMPLING_FACTORS.map((value, idx) => (
                            < option
                        key = {idx}
                        name = "eng2SubsamplingFactor"
                        value = {value} > {value}
                            < /option>
                    ))
                    }
                <
                    /Form.Control>
                    < Form.Control.Feedback
                    type = "invalid" >
                        {errors.eng2SubsamplingFactor}
                        < /Form.Control.Feedback>
                        < /Form.Group> : null}
                        < Form.Group
                    controlId = "formSandboxClusterMode" >
                        < Form.Label > Cluster
                    mode < /Form.Label>
                    < Form.Control
                    as = "select"
                    name = "clusterMode"
                    value = {values.clusterMode}
                    onChange = {handleChange}
                    isInvalid = {
                    !!errors.clusterMode
                }>
                    {
                        CLUSTER_MODES.map(({value, label}, idx) => (
                            < option
                        key = {idx}
                        name = "clusterMode"
                        value = {value} > {label} < /option>
                    ))
                    }
                <
                    /Form.Control>
                    < Form.Control.Feedback
                    type = "invalid" >
                        {errors.clusterMode}
                        < /Form.Control.Feedback>
                        < /Form.Group>
                        < Form.Group
                    className = {values.clusterMode === '0' ? "d-none" : null}
                    controlId = "formSandboxNumSpeakers" >
                        < Form.Label > Speakers < /Form.Label>
                        < Form.Control
                    type = "number"
                    name = "numSpeakers"
                    value = {values.numSpeakers}
                    min = {1}
                    disabled = {values.clusterMode === '0'}
                    onChange = {handleChange}
                    isInvalid = {
                    !!errors.numSpeakers
                }
                    />
                    < Form.Control.Feedback
                    type = "invalid" >
                        {errors.numSpeakers}
                        < /Form.Control.Feedback>
                        < /Form.Group>
                        < Form.Group
                    controlId = "formSandboxFile" >
                        < Form.Label > Audio
                    File(s) < /Form.Label>
                    < Dropzone
                    accept = {SUPPORTED_FORMATS.join(',')}
                    onDrop = {(acceptedFiles)
                =>
                    {
                        // do nothing if no files
                        if (acceptedFiles.length === 0) {
                            return;
                        }

                        const knownFiles = new Set((values.files || [])
                            .map(({lastModified, name}) => `${name}||${lastModified}`)
                        );

                        const files = [...values.files];
                        for (const file of acceptedFiles) {
                            const {name, lastModified} = file;
                            if (knownFiles.has(`${name}||${lastModified}`)) {
                                continue;
                            }
                            files.push(file);
                        }

                        setFieldValue('files', files);
                    }
                }>
                    {
                        ({getRootProps, getInputProps}) => (
                            < div
                        className = {
                            classNames(
                                style['dropzone-container'],
                            'form-control',
                        !!errors.files ? 'is-invalid' : null
                    )
                    }>
                    <
                        div
                        {...
                            getRootProps({
                                className: style['dropzone']
                            })
                        }
                    >
                    <
                        input
                        {...
                            getInputProps()
                        }
                        />
                        {
                            !values || !values.files || values.files.length === 0 ?
                        <
                            p >
                            Drag
                            'n'
                            drop
                            some
                            files
                            here,
                                or
                            click
                            to
                            select
                            files
                            < /p> :
                            < ul >
                            {
                                values.files.map((file, i) => (
                                    < li key = {i} > {file.name} < /li>
                        ))
                        }
                        <
                            /ul>}
                            < /div>
                            < /div>
                        )
                    }
                <
                    /Dropzone>
                    < Form.Control.Feedback
                    type = "invalid" >
                        {errors.files}
                        < /Form.Control.Feedback>
                        < /Form.Group>
                        < Form.Group >
                        < Button
                    variant = "primary"
                    type = "submit"
                    disabled = {submitting} >
                        Upload
                    Audio
                    File
                    < /Button>
                    < /Form.Group>
                    < /Form>
                )
    )
    }
    <
        /Formik>
        < /Col>
        < /Row>;
    }

}

function mapState(state) {
    const {submitting, error} = state.audioDecode;
    return {submitting, error};
}

const actionCreators = {
    decodeAudio: audioActions.decodeAudio
};

export default connect(mapState, actionCreators)(SandboxPage);
