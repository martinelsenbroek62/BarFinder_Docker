import React from 'react';
import {Router, Route} from 'react-router-dom';
import Jumbotron from 'react-bootstrap/Jumbotron';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

import {history} from '../_helpers';
import {PrivateRoute, NavbarComponent} from '../_components';

import SignInPage from '../SignInPage';
import SignOutPage from '../SignOutPage';
import SandboxPage from '../SandboxPage';
import SandboxResultPage from '../SandboxResultPage';
import UsageStatPage from '../UsageStatPage';

import style from './style.module.scss';


export default class App extends React.Component {

    render() {
        return
    <
        Router
        history = {history} >
            < NavbarComponent / >
            < Jumbotron
        className = {style.App} >
            < Container >
            < Row >
            < Col
        sm = {
        {
            span: 8, offset
        :
            2
        }
    }>
    <
        PrivateRoute
        exact
        path = "/" / >
            < Route
        path = "/signin"
        component = {SignInPage}
        />
        < Route
        path = "/signout"
        component = {SignOutPage}
        />
        < PrivateRoute
        exact
        path = "/sandbox"
        component = {SandboxPage}
        />
        < PrivateRoute
        exact
        path = "/usage-stat"
        component = {UsageStatPage}
        />
        < PrivateRoute
        path = "/sandbox/result"
        component = {SandboxResultPage}
        />
        < /Col>
        < /Row>
        < /Container>
        < /Jumbotron>
        < /Router>;
    }

}
