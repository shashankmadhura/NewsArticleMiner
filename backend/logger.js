const winston = require('winston');
const DailyRotateFile = require('winston-daily-rotate-file');

// Configure Winston logger
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console(), // Log to console
    new DailyRotateFile({
      dirname: 'logs', // Directory to store log files
      filename: 'backend-%DATE%.log', // Log file name format
      datePattern: 'YYYY-MM-DD', // Log file rotation pattern
      zippedArchive: true, // Archive log files
      maxSize: '20m', // Max size per log file
      maxFiles: '7d', // Max number of log files to keep
    }),
  ],
});

module.exports = logger