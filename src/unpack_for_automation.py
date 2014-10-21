import json, shutil, sys, os, tarfile, zipfile


class SubmissionError(Exception):
    def __init__(self, submission_file, problem):
        self.submission_file = submission_file
        self.problem = problem

    def __str__(self):
        return '%s:  %s' % (self.submission_file, self.problem)


class SubmissionWarning(Exception):
    def __init__(self, submission_file, problem):
        self.submission_file = submission_file
        self.problem = problem

    def __str__(self):
        return '%s:  %s' % (self.submission_file, self.problem)


def load_spec_file(spec_filename):
    '''
    Load the specified assignment specification file, so that we can figure
    out what filenames we should look for in student submissions.
    '''
    with open(spec_filename) as f:
        return json.load(f)


def process_submission(moodle_filename, files_to_extract, warnings):
    initial_warnings = len(warnings)

    moodle_parts = moodle_filename.split('_')
    if len(moodle_parts) != 3:
        raise SubmissionError(moodle_filename, 'Can\'t parse Moodle archive ' \
            'name.  Does the student\'s filename contain underscores?')

    student_name = moodle_parts[0]

    filename_parts = moodle_parts[1].split('-')

    if len(filename_parts) != 2:
        raise SubmissionError(moodle_filename, 'Can\'t parse student ' \
            'submission filename.')

    username = None
    hwname = None
    if filename_parts[0].startswith('cs121'):
        hwname = filename_parts[0]
        username = filename_parts[1]
    elif filename_parts[1].startswith('cs121'):
        hwname = filename_parts[1]
        username = filename_parts[0]
    else:
        raise SubmissionError(moodle_filename, 'Student submission filename ' \
            'doesn\'t seem to follow required naming convention.')

    # This is where the files will be extracted to.
    target_path = 'students/%s-%s' % (username, hwname)

    # print('Username = "%s", HW name = "%s"' % (username, hwname))
    # print('Target path = "%s"' % target_path)

    if not os.path.isdir(target_path):
        os.makedirs(target_path)

    extension_parts = moodle_parts[2].split('.')
    extension = '.'.join(extension_parts[1:])

    # print('Extension = "%s"' % extension)

    if tarfile.is_tarfile(moodle_filename):

        if not extension in ['tar', 'tar.gz', 'tgz', 'tar.bz2', 'tbz']:
            warnings.append(SubmissionWarning(moodle_filename, 'Tar file ' \
                'submission doesn\'t have a suitable extension!'))

        try:
            archive = tarfile.open(moodle_filename)
        except tarfile.TarError as e:
            raise SubmissionError(moodle_filename, 'Couldn\'t open tar ' \
                'archive, reason:  ' + str(e))

        # print('Archive file names:  %s' % str(archive.getnames()))

        for fname in files_to_extract:
            try:
                extract_tar_member(moodle_filename, archive, fname, target_path)
            except SubmissionWarning as w:
                warnings.append(w)

        archive.close()

    elif zipfile.is_zipfile(moodle_filename):

        if extension != 'zip' or \
           (extension.endswith('.zip') and extension.contains('tgz')):
            warnings.append(SubmissionWarning(moodle_filename, 'Zip file ' \
                'submission doesn\'t have a suitable extension!'))

        archive = zipfile.ZipFile(moodle_filename)

        # print('Archive file names:  %s' % str(archive.namelist()))

        for fname in files_to_extract:
            try:
                extract_zip_member(moodle_filename, archive, fname, target_path)
            except SubmissionWarning as w:
                warnings.append(w)

        archive.close()

    else:
        raise SubmissionError(moodle_filename, 'Unrecognized archive format')

    if len(warnings) == initial_warnings:
        print('Successfully processed submission:  %s' % moodle_filename)
    else:
        print('Encountered WARNINGS on submission:  %s' % moodle_filename)


def extract_tar_member(moodle_filename, archive, fname, target_path):
    member = None
    for m in archive.getmembers():
        if not m.isfile():
            continue

        m_name = m.name.split('/')[-1]
        if m_name == fname:
            if member is not None:
                raise SubmissionError(moodle_filename, 'Archive contains ' \
                    'multiple copies of file "%s"!' % fname)

            member = m

    if member is None:
        raise SubmissionWarning(moodle_filename, 'Archive doesn\'t contain ' \
            'required file "%s"!' % fname)

    src_file = archive.extractfile(member)
    dst_file = open(target_path + '/' + fname, 'w')
    shutil.copyfileobj(src_file, dst_file)
    src_file.close()
    dst_file.close()


def extract_zip_member(moodle_filename, archive, fname, target_path):
    member = None
    for m in archive.infolist():
        m_name = m.filename.split('/')[-1]
        if m_name == fname:
            if member is not None:
                raise SubmissionError(moodle_filename, 'Archive contains ' \
                    'multiple copies of file "%s"!' % fname)

            member = m

    if member is None:
        raise SubmissionWarning(moodle_filename, 'Archive doesn\'t contain ' \
            'required file "%s"!' % fname)

    src_file = archive.open(member)
    dst_file = open(target_path + '/' + fname, 'w')
    shutil.copyfileobj(src_file, dst_file)
    src_file.close()
    dst_file.close()


if __name__ == '__main__':
    spec_filename = sys.argv[1]

    print('Loading specification file "%s".' % spec_filename)
    spec_json = load_spec_file(spec_filename)
    files_to_extract = spec_json.get('files', [])
    if len(files_to_extract) == 0:
        print('ERROR:  No submission files specified!')
        sys.exit(1)

    print('Files to extract from submissions:  %s' % \
        (', '.join(files_to_extract)))
    print

    moodle_filenames = sys.stdin.readlines()
    moodle_filenames = set(moodle_filenames)
    moodle_filenames = list(moodle_filenames)
    moodle_filenames.sort()

    bad_lines = []
    warnings = []

    for line in moodle_filenames:
        line = line.strip()
        if len(line) == 0:
            continue

        try:
            process_submission(line, files_to_extract, warnings)
        except SubmissionError as e:
            bad_lines.append(str(e))

    if len(bad_lines) > 0:
        print('\nCould not process these submissions:')
        for line in bad_lines:
            print(' * %s' % line)

    if len(warnings) > 0:
        print('\nThese warnings were generated:')
        for warn in warnings:
            print(' * %s' % str(warn))

