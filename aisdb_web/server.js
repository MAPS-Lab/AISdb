import { __dirname, start_interface } from './server_module.js';
import express from 'express';

// app config
const app = express();
const port = 8080;

app.use('/', express.static(`${__dirname }/dist_map`));

start_interface(app, port);

