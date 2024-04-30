import {Box, Heading, PageHeader, Subtitle, TextInput} from '@dagster-io/ui-components';
import * as React from 'react';

import {InstancePageContext} from './InstancePageContext';
import {InstanceTabs} from './InstanceTabs';
import {flattenCodeLocationRows} from './flattenCodeLocationRows';
import {useTrackPageView} from '../app/analytics';
import {useDocumentTitle} from '../hooks/useDocumentTitle';
import {ReloadAllButton} from '../workspace/ReloadAllButton';
import {RepositoryLocationsList} from '../workspace/RepositoryLocationsList';
import {WorkspaceContext} from '../workspace/WorkspaceContext';

const SEARCH_THRESHOLD = 10;

export const CodeLocationsPageContent = () => {
  useTrackPageView();
  useDocumentTitle('Code locations');

  const {locationEntries, loading} = React.useContext(WorkspaceContext);

  const [searchValue, setSearchValue] = React.useState('');

  const onChangeSearch = React.useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchValue(e.target.value);
  }, []);

  const queryString = searchValue.toLocaleLowerCase();
  const {flattened, filtered} = React.useMemo(() => {
    return flattenCodeLocationRows(locationEntries, queryString);
  }, [locationEntries, queryString]);

  const entryCount = flattened.length;
  const showSearch = entryCount > SEARCH_THRESHOLD;

  const SubtitleText = () => {
    if (loading || !entryCount) {
      return 'Code locations';
    }

    return entryCount === 1 ? '1 code location' : `${entryCount} code locations`;
  };

  return (
    <>
      <Box
        padding={{vertical: 16, horizontal: 24}}
        flex={{direction: 'row', justifyContent: 'space-between', alignItems: 'center'}}
        style={{height: '64px'}}
      >
        {showSearch ? (
          <TextInput
            icon="search"
            value={searchValue}
            onChange={onChangeSearch}
            placeholder="Filter code locations by name…"
            style={{width: '400px'}}
          />
        ) : (
          <Subtitle id="repository-locations">{SubtitleText()}</Subtitle>
        )}
        <Box flex={{direction: 'row', gap: 12, alignItems: 'center'}}>
          {showSearch ? <div>{`${entryCount} code locations`}</div> : null}
          <ReloadAllButton />
        </Box>
      </Box>
      <RepositoryLocationsList
        loading={loading}
        codeLocations={filtered}
        searchValue={searchValue}
      />
    </>
  );
};

export const CodeLocationsPage = () => {
  const {pageTitle} = React.useContext(InstancePageContext);
  return (
    <Box flex={{direction: 'column'}} style={{height: '100%', overflow: 'hidden'}}>
      <PageHeader title={<Heading>{pageTitle}</Heading>} tabs={<InstanceTabs tab="locations" />} />
      <CodeLocationsPageContent />
    </Box>
  );
};

// Imported via React.lazy, which requires a default export.
// eslint-disable-next-line import/no-default-export
export default CodeLocationsPage;
