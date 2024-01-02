import axios from 'axios';
import { CONFIG } from './DB_CONFIG.js';

/**
* JavaScript wrapper for interacting with the FastAPI API.
*/
export class APIWrapper {
    constructor() {
        this.baseURL = `http://${CONFIG.ip}:${CONFIG.port}`;
    }
    /**
    * Create a new experiment.
    * @param {Object} experimentData - Data for creating a new experiment.
    * @returns {Promise<Object>} - Resolves to an object containing the created experiment's UUID.
    */
    async createExperiment(experimentData) {
        try {
            const response = await axios.post(`${this.baseURL}/createExperiment/`, experimentData);
            return response.data;
        } catch (error) {
            console.error('Error creating experiment:', error);
            throw error;
        }
    }
    
    /**
    * Insert data into an experiment's table.
    * @param {string} uuid - UUID of the experiment's table.
    * @param {Object} data - Data to be inserted into the table.
    * @returns {Promise<Object>} - Resolves to a success message.
    */
    async insertData(uuid, data) {
        try {
            const response = await axios.post(`${this.baseURL}/insertData/${uuid}`, data);
            return response.data;
        } catch (error) {
            console.error('Error inserting data:', error);
            throw error;
        }
    }
    
    /**
    * Get column information for an experiment's table.
    * @param {string} uuid - UUID of the experiment's table.
    * @returns {Promise<Object>} - Resolves to column information.
    */
    async getColumns(uuid) {
        try {
            const response = await axios.post(`${this.baseURL}/getColumns/${uuid}`);
            return response.data;
        } catch (error) {
            console.error('Error getting columns:', error);
            throw error;
        }
    }
    
    /**
    * Read data from an experiment's table.
    * @param {string} uuid - UUID of the experiment's table.
    * @param {number} num - (Optional) Maximum number of rows to retrieve.
    * @param {number} start - (Optional) Start parameter for filtering rows.
    * @param {number} stop - (Optional) Stop parameter for filtering rows.
    * @returns {Promise<Array>} - Resolves to an array of data rows from the table.
    */
    async readData(uuid, num, start, stop) {
        try {
            const response = await axios.get(`${this.baseURL}/readData`, {
                params: { uuid, num, start, stop },
            });
            return response.data;
        } catch (error) {
            console.error('Error reading data:', error);
            throw error;
        }
    }
    
    /**
    * Get tags associated with experiments.
    * @param {string} tag - (Optional) Tag identifier to filter experiments.
    * @returns {Promise<Array>} - Resolves to an array of objects containing UUID and tag information.
    */
    async getTags(tag) {
        try {
            const response = await axios.get(`${this.baseURL}/getTags`, {
                params: { tag },
            });
            return response.data;
        } catch (error) {
            console.error('Error getting tags:', error);
            throw error;
        }
    }
}
