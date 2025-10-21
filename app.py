from flask import Flask, render_template_string, jsonify, Response, request
import requests
import json
import csv
from io import StringIO
from datetime import datetime

app = Flask(__name__)

# Store fetched data in memory
job_data = []

DEPARTMENTS = [
    {'code': 'AG', 'name': 'Department of Agriculture', 'acronym': 'USDA'},
    {'code': 'CI', 'name': 'Central Intelligence Agency', 'acronym': 'CIA'},
    {'code': 'CM', 'name': 'Department of Commerce', 'acronym': 'DOC'},
    {'code': 'DD', 'name': 'Department of Defense', 'acronym': 'DOD'},
    {'code': 'ED', 'name': 'Department of Education', 'acronym': 'ED'},
    {'code': 'DN', 'name': 'Department of Energy', 'acronym': 'DOE'},
    {'code': 'EP', 'name': 'Environmental Protection Agency', 'acronym': 'EPA'},
    {'code': 'HE', 'name': 'Department of Health and Human Services', 'acronym': 'HHS'},
    {'code': 'HS', 'name': 'Department of Homeland Security', 'acronym': 'DHS'},
    {'code': 'HU', 'name': 'Department of Housing and Urban Development', 'acronym': 'HUD'},
    {'code': 'IN', 'name': 'Department of the Interior', 'acronym': 'DOI'},
    {'code': 'DJ', 'name': 'Department of Justice', 'acronym': 'DOJ'},
    {'code': 'DL', 'name': 'Department of Labor', 'acronym': 'DOL'},
    {'code': 'OI', 'name': 'Office of the Director of National Intelligence', 'acronym': 'ODNI'},
    {'code': 'SZ', 'name': 'Social Security Administration', 'acronym': 'SSA'},
    {'code': 'ST', 'name': 'Department of State', 'acronym': 'DOS'},
    {'code': 'TD', 'name': 'Department of Transportation', 'acronym': 'DOT'},
    {'code': 'TR', 'name': 'Department of the Treasury', 'acronym': 'Treasury'},
    {'code': 'VA', 'name': 'Department of Veterans Affairs', 'acronym': 'VA'},
    {'code': 'OM', 'name': 'Office of Personnel Management', 'acronym': 'OPM'},
    {'code': 'GS', 'name': 'General Services Administration', 'acronym': 'GSA'},
    {'code': 'NN', 'name': 'National Aeronautics and Space Administration', 'acronym': 'NASA'},
    {'code': 'SB', 'name': 'Small Business Administration', 'acronym': 'SBA'},
    {'code': 'NF', 'name': 'National Science Foundation', 'acronym': 'NSF'}
]

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Federal Job Data Analytics Platform</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        body {
            background: #0a0e27;
            color: #e4e4e7;
        }

        .top-bar {
            background: linear-gradient(to right, #1e293b, #0f172a);
            border-bottom: 1px solid #334155;
        }

        .section {
            background: #0f172a;
            border: 1px solid #1e293b;
        }

        .stat-box {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border-left: 3px solid #3b82f6;
        }

        .btn {
            font-weight: 500;
            letter-spacing: 0.025em;
            transition: all 0.2s;
        }

        .btn-primary {
            background: #3b82f6;
            color: white;
        }

        .btn-primary:hover:not(:disabled) {
            background: #2563eb;
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.4);
        }

        .btn-secondary {
            background: #1e293b;
            color: #94a3b8;
            border: 1px solid #334155;
        }

        .btn-secondary:hover:not(:disabled) {
            background: #334155;
            color: #e4e4e7;
            border-color: #475569;
        }

        .console {
            background: #020617;
            border: 1px solid #1e293b;
            font-family: 'Courier New', monospace;
        }

        .status-indicator {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #22c55e;
            box-shadow: 0 0 10px #22c55e;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .data-label {
            color: #64748b;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }

        .data-value {
            color: #f1f5f9;
            font-size: 2.5rem;
            font-weight: 300;
            line-height: 1;
        }

        .dept-checkbox {
            appearance: none;
            width: 18px;
            height: 18px;
            border: 2px solid #334155;
            border-radius: 3px;
            background: #0f172a;
            cursor: pointer;
            position: relative;
        }

        .dept-checkbox:checked {
            background: #3b82f6;
            border-color: #3b82f6;
        }

        .dept-checkbox:checked::after {
            content: '✓';
            position: absolute;
            color: white;
            font-size: 12px;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th {
            background: #1e293b;
            color: #94a3b8;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid #334155;
            position: sticky;
            top: 0;
            z-index: 10;
        }

        td {
            padding: 12px;
            border-bottom: 1px solid #1e293b;
            color: #cbd5e1;
            font-size: 0.875rem;
        }

        tr:hover {
            background: #1e293b;
        }

        input[type="date"] {
            background: #1e293b;
            border: 1px solid #334155;
            color: #e4e4e7;
            padding: 8px 12px;
            border-radius: 4px;
        }

        input[type="date"]:focus {
            outline: none;
            border-color: #3b82f6;
        }

        .pagination {
            display: flex;
            gap: 8px;
            align-items: center;
            justify-content: center;
            padding: 16px;
        }

        .page-btn {
            padding: 8px 12px;
            background: #1e293b;
            border: 1px solid #334155;
            color: #94a3b8;
            cursor: pointer;
            border-radius: 4px;
            font-size: 0.875rem;
        }

        .page-btn:hover:not(:disabled) {
            background: #334155;
            color: #e4e4e7;
        }

        .page-btn.active {
            background: #3b82f6;
            color: white;
            border-color: #3b82f6;
        }

        .page-btn:disabled {
            opacity: 0.4;
            cursor: not-allowed;
        }

        /* Progress Bar Styles */
        .progress-container {
            background: #1e293b;
            border-radius: 8px;
            overflow: hidden;
            height: 8px;
            position: relative;
        }

        .progress-bar {
            background: linear-gradient(90deg, #3b82f6, #60a5fa);
            height: 100%;
            width: 0%;
            transition: width 0.3s ease;
            border-radius: 8px;
        }

        .progress-text {
            color: #94a3b8;
            font-size: 0.875rem;
            margin-top: 8px;
            text-align: center;
        }
    </style>
</head>
<body class="min-h-screen">
    <!-- Top Bar -->
    <div class="top-bar px-6 py-4">
        <div class="max-w-7xl mx-auto flex items-center justify-between">
            <div class="flex items-center gap-4">
                <div class="status-indicator"></div>
                <div>
                    <h1 class="text-xl font-semibold text-white">FEDERAL JOB DATA ANALYTICS</h1>
                    <p class="text-sm text-slate-400">Historical Intelligence System</p>
                </div>
            </div>
        </div>
    </div>

    <div class="max-w-7xl mx-auto p-6 space-y-6">

        <!-- Filters -->
        <div class="section rounded-lg p-6">
            <div class="text-xs text-slate-400 uppercase tracking-wider mb-4 font-semibold">Filters</div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Date Range -->
                <div>
                    <div class="data-label mb-3">Date Period</div>
                    <div class="flex gap-3">
                        <div class="flex-1">
                            <label class="text-xs text-slate-500 mb-1 block">Start Date</label>
                            <input type="date" id="startDate" value="2025-01-21" class="w-full">
                        </div>
                        <div class="flex-1">
                            <label class="text-xs text-slate-500 mb-1 block">End Date</label>
                            <input type="date" id="endDate" value="2025-10-18" class="w-full">
                        </div>
                    </div>
                </div>

                <!-- Department Selection -->
                <div>
                    <div class="flex items-center justify-between mb-3">
                        <div class="data-label">Departments</div>
                        <button onclick="toggleSelectAll()" class="text-xs text-blue-400 hover:text-blue-300 cursor-pointer">
                            Select All / None
                        </button>
                    </div>
                    <div class="grid grid-cols-3 gap-2 p-3 bg-slate-900 rounded">
                        ''' + ''.join([f'''
                        <label class="flex items-center gap-2 text-sm cursor-pointer hover:text-white">
                            <input type="checkbox" class="dept-checkbox" value="{dept['code']}" {' checked' if dept['code'] == 'AG' else ''}>
                            <span>{dept['acronym']}</span>
                        </label>
                        ''' for dept in DEPARTMENTS]) + '''
                    </div>
                </div>
            </div>
        </div>

        <!-- Control Panel -->
        <div class="section rounded-lg p-6">
            <div class="text-xs text-slate-400 uppercase tracking-wider mb-4 font-semibold">Control Panel</div>
            <div class="flex gap-3 flex-wrap">
                <button id="fetchBtn" onclick="fetchJobs()" class="btn btn-primary px-6 py-2.5 rounded disabled:opacity-40 disabled:cursor-not-allowed">
                    RETRIEVE DATA
                </button>
                <button id="exportCsvBtn" onclick="exportCSV()" disabled class="btn btn-secondary px-6 py-2.5 rounded disabled:opacity-40 disabled:cursor-not-allowed">
                    EXPORT CSV
                </button>
                <button onclick="clearConsole()" class="btn btn-secondary px-6 py-2.5 rounded ml-auto">
                    CLEAR LOG
                </button>
            </div>
        </div>

        <!-- Progress Bar -->
        <div id="progressSection" class="section rounded-lg p-6 hidden">
            <div class="data-label mb-3">Fetching Progress</div>
            <div class="progress-container">
                <div id="progressBar" class="progress-bar"></div>
            </div>
            <div id="progressText" class="progress-text">Initializing...</div>
        </div>

        <!-- Stats -->
        <div class="grid grid-cols-2 gap-6">
            <div class="stat-box section rounded-lg p-6">
                <div class="data-label mb-2">Total Positions</div>
                <div id="jobCount" class="data-value">0</div>
            </div>
            <div class="stat-box section rounded-lg p-6">
                <div class="data-label mb-2">Data Pages Retrieved</div>
                <div id="pageCount" class="data-value">0</div>
            </div>
        </div>

        <!-- Data Preview -->
        <div id="dataPreview" class="section rounded-lg overflow-hidden hidden">
            <div class="px-6 py-3 bg-slate-900 border-b border-slate-800">
                <div class="text-xs text-slate-400 uppercase tracking-wider font-semibold">Data Preview (Sorted by Posted Date - Newest First)</div>
            </div>
            <div class="overflow-x-auto" style="max-height: 600px; overflow-y: auto;">
                <table id="dataTable">
                    <thead>
                        <tr>
                            <th>Position Title</th>
                            <th>Department</th>
                            <th>Agency</th>
                            <th>Position Status</th>
                            <th>Location</th>
                            <th>Salary Min</th>
                            <th>Salary Max</th>
                            <th>Grade</th>
                            <th>Posted Date</th>
                            <th>Close Date</th>
                        </tr>
                    </thead>
                    <tbody id="tableBody"></tbody>
                </table>
            </div>
            <div class="pagination">
                <button onclick="changePage(-1)" id="prevBtn" class="page-btn" disabled>← Previous</button>
                <span id="pageInfo" class="text-sm" style="color: #94a3b8;">Page 1 of 1</span>
                <button onclick="changePage(1)" id="nextBtn" class="page-btn" disabled>Next →</button>
            </div>
        </div>

        <!-- Console -->
        <div class="section rounded-lg overflow-hidden">
            <div class="px-6 py-3 bg-slate-900 border-b border-slate-800">
                <div class="text-xs text-slate-400 uppercase tracking-wider font-semibold">System Log</div>
            </div>
            <div class="console p-4 h-64 overflow-y-auto text-sm">
                <div id="console"></div>
            </div>
        </div>

    </div>

    <script>
        let allJobsData = [];
        let currentPage = 1;
        const jobsPerPage = 50;

        function toggleSelectAll() {
            const checkboxes = document.querySelectorAll('.dept-checkbox');
            const allChecked = Array.from(checkboxes).every(cb => cb.checked);

            checkboxes.forEach(cb => {
                cb.checked = !allChecked;
            });
        }

        function addLog(message, type = 'info') {
            const console = document.getElementById('console');
            const timestamp = new Date().toLocaleTimeString('en-US', { hour12: false });
            const colors = {
                info: '#60a5fa',
                success: '#34d399',
                error: '#f87171',
                warning: '#fbbf24'
            };
            const line = document.createElement('div');
            line.style.color = colors[type] || colors.info;
            line.style.marginBottom = '4px';
            line.innerHTML = `<span style="color: #64748b;">[${timestamp}]</span> ${message}`;
            console.appendChild(line);
            console.parentElement.scrollTop = console.parentElement.scrollHeight;
        }

        function clearConsole() {
            document.getElementById('console').innerHTML = '';
            document.getElementById('jobCount').textContent = '0';
            document.getElementById('pageCount').textContent = '0';
            document.getElementById('dataPreview').classList.add('hidden');
            document.getElementById('progressSection').classList.add('hidden');
            allJobsData = [];
            currentPage = 1;
        }

        function updateProgress(current, total, message) {
            const progressSection = document.getElementById('progressSection');
            const progressBar = document.getElementById('progressBar');
            const progressText = document.getElementById('progressText');

            progressSection.classList.remove('hidden');
            const percentage = (current / total) * 100;
            progressBar.style.width = percentage + '%';
            progressText.textContent = message || `Processing ${current} of ${total} departments...`;
        }

        function changePage(direction) {
            const totalPages = Math.ceil(allJobsData.length / jobsPerPage);
            currentPage += direction;

            if (currentPage < 1) currentPage = 1;
            if (currentPage > totalPages) currentPage = totalPages;

            updateTable();
        }

        function updateTable() {
            const tbody = document.getElementById('tableBody');
            tbody.innerHTML = '';

            const totalPages = Math.ceil(allJobsData.length / jobsPerPage);
            const startIdx = (currentPage - 1) * jobsPerPage;
            const endIdx = startIdx + jobsPerPage;
            const pageData = allJobsData.slice(startIdx, endIdx);

            pageData.forEach(job => {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${job['Position Title']}</td>
                    <td>${job['Department']}</td>
                    <td>${job['Agency']}</td>
                    <td>${job['Position Status']}</td>
                    <td>${job['Location']}</td>
                    <td>${job['Salary Min']}</td>
                    <td>${job['Salary Max']}</td>
                    <td>${job['Grade Min']}-${job['Grade Max']}</td>
                    <td>${job['Posted Date']}</td>
                    <td>${job['Close Date']}</td>
                `;
            });

            // Update pagination controls
            document.getElementById('pageInfo').textContent = `Page ${currentPage} of ${totalPages}`;
            document.getElementById('prevBtn').disabled = currentPage === 1;
            document.getElementById('nextBtn').disabled = currentPage === totalPages;

            if (allJobsData.length > 0) {
                document.getElementById('dataPreview').classList.remove('hidden');
            }
        }

        async function fetchJobs() {
            const fetchBtn = document.getElementById('fetchBtn');
            const exportCsvBtn = document.getElementById('exportCsvBtn');

            // Get selected departments
            const selectedDepts = Array.from(document.querySelectorAll('.dept-checkbox:checked'))
                .map(cb => cb.value);

            if (selectedDepts.length === 0) {
                addLog('Please select at least one department', 'error');
                return;
            }

            // Get dates
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;

            fetchBtn.disabled = true;
            exportCsvBtn.disabled = true;
            fetchBtn.textContent = 'PROCESSING...';

            addLog('Initializing data retrieval from USAJobs API...', 'info');
            addLog(`Departments: ${selectedDepts.join(', ')}`, 'info');
            addLog(`Date range: ${startDate} to ${endDate}`, 'info');

            updateProgress(0, selectedDepts.length, 'Starting...');

            try {
                const response = await fetch('/fetch_jobs', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        departments: selectedDepts,
                        startDate: startDate,
                        endDate: endDate
                    })
                });

                const data = await response.json();

                if (data.status === 'success') {
                    data.logs.forEach(log => {
                        addLog(log.message, log.type);
                    });

                    // Update progress indicators
                    data.progress.forEach((prog, idx) => {
                        updateProgress(idx + 1, selectedDepts.length, prog.message);
                    });

                    updateProgress(selectedDepts.length, selectedDepts.length, 'Complete!');

                    document.getElementById('jobCount').textContent = data.job_count.toLocaleString();
                    document.getElementById('pageCount').textContent = data.page_count;
                    exportCsvBtn.disabled = false;

                    // Store all jobs data (already sorted by backend)
                    allJobsData = data.all_data;
                    currentPage = 1;
                    updateTable();

                    // Hide progress bar after a delay
                    setTimeout(() => {
                        document.getElementById('progressSection').classList.add('hidden');
                    }, 3000);
                } else {
                    addLog(`Error: ${data.message}`, 'error');
                    if (data.logs) {
                        data.logs.forEach(log => {
                            addLog(log.message, log.type);
                        });
                    }
                    document.getElementById('progressSection').classList.add('hidden');
                }
            } catch (error) {
                addLog(`Error: ${error.message}`, 'error');
                document.getElementById('progressSection').classList.add('hidden');
            } finally {
                fetchBtn.disabled = false;
                fetchBtn.textContent = 'RETRIEVE DATA';
            }
        }

        function exportCSV() {
            addLog('Generating CSV export...', 'info');
            window.location.href = '/export_csv';
            addLog('CSV download initiated', 'success');
        }
    </script>
</body>
</html>
'''


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/fetch_jobs', methods=['POST'])
def fetch_jobs():
    global job_data
    job_data = []
    logs = []
    progress = []

    data = request.json
    departments = data.get('departments', [])
    start_date = data.get('startDate', '2025-01-21')
    end_date = data.get('endDate', '2025-10-18')

    base_url = 'https://data.usajobs.gov/api/historicjoa'
    headers = {
        'User-Agent': 'nikola.d.misetic@gmail.com',
        'Authorization-Key': '2sdQC2rtq3ovRY4J2wNFb1XDzFqiqQcW8tKSOygnD8A='
    }

    all_jobs = []
    page_count = 0

    try:
        logs.append({'message': '===== STARTING FETCH =====', 'type': 'success'})
        logs.append({'message': f'Departments: {", ".join(departments)}', 'type': 'info'})
        logs.append({'message': f'Date range: {start_date} to {end_date}', 'type': 'info'})

        for idx, dept_code in enumerate(departments):
            dept_name = next((d['acronym'] for d in DEPARTMENTS if d['code'] == dept_code), dept_code)
            logs.append({'message': f'--- Fetching {dept_name} ({idx + 1}/{len(departments)}) ---', 'type': 'info'})
            progress.append({'current': idx + 1, 'total': len(departments), 'message': f'Fetching {dept_name}...'})

            next_url = None
            page = 1

            params = {
                'HiringDepartmentCodes': dept_code,
                'StartPositionOpenDate': start_date,
                'EndPositionOpenDate': end_date
            }

            while True:
                try:
                    if next_url:
                        full_url = f'https://data.usajobs.gov{next_url}'
                        response = requests.get(full_url, headers=headers, timeout=30)
                    else:
                        response = requests.get(base_url, headers=headers, params=params, timeout=30)

                    if response.status_code == 200:
                        # Get raw text first
                        response_text = response.text.strip()

                        # Check if response is empty
                        if not response_text:
                            logs.append({'message': f'⚠ Empty response from API for {dept_name}', 'type': 'warning'})
                            break

                        # Check if response looks like JSON
                        if not response_text.startswith('{'):
                            logs.append({'message': f'⚠ Invalid JSON response for {dept_name}', 'type': 'warning'})
                            logs.append({'message': f'Response preview: {response_text[:100]}...', 'type': 'warning'})
                            break

                        # Try to parse JSON
                        try:
                            api_data = json.loads(response_text)
                        except json.JSONDecodeError as je:
                            logs.append({'message': f'JSON ERROR for {dept_name}: {str(je)}', 'type': 'error'})
                            logs.append({'message': f'Error at position {je.pos}', 'type': 'error'})
                            logs.append({'message': f'Response preview: {response_text[:200]}...', 'type': 'error'})
                            break

                        jobs = api_data.get('data', [])

                        if not jobs:
                            logs.append(
                                {'message': f'No more jobs found for {dept_name} on page {page}', 'type': 'info'})
                            break

                        all_jobs.extend(jobs)
                        page_count += 1
                        logs.append({'message': f'✓ {dept_name} Page {page}: {len(jobs)} jobs | Total: {len(all_jobs)}',
                                     'type': 'success'})

                        paging = api_data.get('paging', {})
                        next_url = paging.get('next')

                        if not next_url:
                            logs.append({'message': f'✓ Completed {dept_name} - no more pages', 'type': 'success'})
                            break

                        page += 1

                    elif response.status_code == 404:
                        logs.append({'message': f'⚠ No data found for {dept_name} (404)', 'type': 'warning'})
                        break
                    else:
                        logs.append(
                            {'message': f'HTTP ERROR for {dept_name}: Status {response.status_code}', 'type': 'error'})
                        logs.append({'message': f'Response: {response.text[:200]}', 'type': 'error'})
                        break

                except requests.exceptions.Timeout:
                    logs.append({'message': f'TIMEOUT for {dept_name} on page {page}', 'type': 'error'})
                    break
                except requests.exceptions.RequestException as re:
                    logs.append({'message': f'REQUEST ERROR for {dept_name}: {str(re)}', 'type': 'error'})
                    break
                except Exception as e:
                    logs.append({'message': f'UNEXPECTED ERROR for {dept_name}: {str(e)}', 'type': 'error'})
                    break

        logs.append({'message': f'===== PROCESSING {len(all_jobs)} JOBS =====', 'type': 'info'})

        for job in all_jobs:
            locations = job.get('positionLocations', [])
            location_str = ', '.join([f"{loc.get('positionLocationCity', '')}, {loc.get('positionLocationState', '')}"
                                      for loc in locations]) if locations else 'N/A'

            categories = job.get('jobCategories', [])
            series_str = ', '.join([cat.get('series', '') for cat in categories]) if categories else 'N/A'

            hiring_paths = job.get('hiringPaths', [])
            paths_str = ', '.join([hp.get('hiringPath', '') for hp in hiring_paths]) if hiring_paths else 'N/A'

            job_data.append({
                'Announcement Number': job.get('announcementNumber', 'N/A'),
                'Control Number': job.get('usajobsControlNumber', 'N/A'),
                'Position Title': job.get('positionTitle', 'N/A'),
                'Department': job.get('hiringDepartmentName', 'N/A'),
                'Agency': job.get('hiringAgencyName', 'N/A'),
                'Position Status': job.get('positionOpeningStatus', 'N/A'),
                'Location': location_str,
                'Salary Min': job.get('minimumSalary', 'N/A'),
                'Salary Max': job.get('maximumSalary', 'N/A'),
                'Pay Scale': job.get('payScale', 'N/A'),
                'Grade Min': job.get('minimumGrade', 'N/A'),
                'Grade Max': job.get('maximumGrade', 'N/A'),
                'Appointment Type': job.get('appointmentType', 'N/A'),
                'Work Schedule': job.get('workSchedule', 'N/A'),
                'Posted Date': job.get('positionOpenDate', 'N/A'),
                'Close Date': job.get('positionCloseDate', 'N/A'),
                'Job Series': series_str,
                'Hiring Paths': paths_str,
                'Telework Eligible': job.get('teleworkEligible', 'N/A'),
                'Travel Required': job.get('travelRequirement', 'N/A'),
                'Security Clearance': job.get('securityClearance', 'N/A'),
                'Who May Apply': job.get('whoMayApply', 'N/A')
            })

        # Sort by Posted Date (newest first)
        def parse_date(date_str):
            if date_str == 'N/A':
                return datetime.min
            try:
                return datetime.strptime(date_str, '%Y-%m-%d')
            except:
                return datetime.min

        job_data.sort(key=lambda x: parse_date(x['Posted Date']), reverse=True)

        logs.append({'message': f'✓ Successfully processed {len(job_data)} jobs', 'type': 'success'})
        logs.append({'message': '✓ Data sorted by Posted Date (newest first)', 'type': 'success'})
        logs.append({'message': '✓ Data ready for export!', 'type': 'success'})

        return jsonify({
            'status': 'success',
            'logs': logs,
            'progress': progress,
            'job_count': len(job_data),
            'page_count': page_count,
            'all_data': job_data
        })

    except Exception as e:
        logs.append({'message': f'EXCEPTION: {str(e)}', 'type': 'error'})
        import traceback
        logs.append({'message': f'Traceback: {traceback.format_exc()}', 'type': 'error'})
        return jsonify({
            'status': 'error',
            'logs': logs,
            'message': str(e)
        })


@app.route('/export_csv')
def export_csv():
    if not job_data:
        return "No data to export. Please fetch data first.", 400

    si = StringIO()
    if job_data:
        fieldnames = job_data[0].keys()
        writer = csv.DictWriter(si, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(job_data)

    output = si.getvalue()
    si.close()

    filename = f'federal_jobs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )


if __name__ == '__main__':
    import os

    port = int(os.environ.get('PORT', 6969))
    app.run(host='0.0.0.0', port=port, debug=False)
