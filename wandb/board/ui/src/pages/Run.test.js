import React from 'react';
import MockAppWrapper from '../util/test/mockAppWrapper';
import {Run} from './Run';
import Loader from '../components/Loader';
import RunViewer from '../components/RunViewer';
import RunEditor from '../components/RunEditor';

describe('Run page components test', () => {
  const store = mockStore({
      global: {},
      views: {
        server: {},
        browser: {
          run: {
            views: [],
            tabs: [],
          },
        },
        other: {
          run: {
            activeView: '',
          },
        },
      },
    }),
    model = {
      bucket: {
        createdAt: '2017-24-09T10:09:28.487559',
        exampleTable: '[]',
        exampleTableColumns: '[]',
        exampleTableTypes: '{}',
        history: [],
        logLines: {
          edges: [],
        },
        summaryMetrics: '{}',
      },
    },
    views = {
      run: {},
    },
    loss = [],
    user = {};
  let container,
    loading = true,
    match = {
      params: {
        run: '',
      },
      path: '/:entity/:model/runs/:run',
    };

  beforeEach(() => {
    container = mount(
      <MockAppWrapper store={store}>
        <Run
          match={match}
          views={views}
          loss={loss}
          user={user}
          loading={loading}
          updateLocationParams={() => {}}
          setBrowserViews={() => {}}
          setServerViews={() => {}}
        />
      </MockAppWrapper>
    );
  });

  it('finds <Loader /> component', () => {
    expect(container.find(Loader)).toHaveLength(1);
  });

  it('finds <RunViewer /> component', () => {
    //TODO: Unfortunate...
    container = mount(
      <MockAppWrapper store={store}>
        <Run
          run={model.bucket}
          project={model}
          match={match}
          views={views}
          loss={loss}
          user={user}
          loading={loading}
          updateLocationParams={() => {}}
          setBrowserViews={() => {}}
          setServerViews={() => {}}
        />
      </MockAppWrapper>
    );
    expect(container.find(RunViewer)).toHaveLength(1);
  });
});
