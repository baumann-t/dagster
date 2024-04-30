import {Button} from '@dagster-io/ui-components';
import * as React from 'react';
import styled from 'styled-components';

import {Markdown} from '../ui/Markdown';

interface IDescriptionProps {
  description: string | null;
  maxHeight?: number;
  fontSize?: string | number;
}

interface IDescriptionState {
  hasMore: boolean;
  expanded: boolean;
}

const DEFAULT_MAX_HEIGHT = 320;

/*
If `input` begins with whitespace and every line contains at least that whitespace,
it removes it. Otherwise, return the original string.
*/
function removeLeadingSpaces(input: string) {
  const leadingSpaces = /^\n?( +)/.exec(input);
  if (leadingSpaces == null) {
    return input;
  }

  const lines = input.split('\n');
  if (!lines.every((l) => l.substr(0, leadingSpaces[1]!.length).trim() === '')) {
    return input;
  }

  return lines.map((l) => l.substr(leadingSpaces[1]!.length)).join('\n');
}

export class Description extends React.Component<IDescriptionProps, IDescriptionState> {
  private _container: React.RefObject<HTMLDivElement> = React.createRef();

  public state: IDescriptionState = {
    hasMore: false,
    expanded: false,
  };

  componentDidMount() {
    this.updateHandleState();
  }

  componentDidUpdate() {
    this.updateHandleState();
  }

  updateHandleState() {
    if (!this._container.current) {
      return;
    }
    const hasMore =
      this._container.current.clientHeight > (this.props.maxHeight || DEFAULT_MAX_HEIGHT);
    if (hasMore !== this.state.hasMore) {
      this.setState({hasMore});
    }
  }

  render() {
    if (!this.props.description || this.props.description.length === 0) {
      return null;
    }

    const {expanded, hasMore} = this.state;
    return (
      <Container
        onDoubleClick={() => {
          const sel = document.getSelection();
          if (!sel || !this._container.current) {
            return;
          }
          const range = document.createRange();
          range.selectNodeContents(this._container.current);
          sel.removeAllRanges();
          sel.addRange(range);
        }}
        $fontSize={this.props.fontSize || '0.8rem'}
        style={{
          maxHeight: expanded ? undefined : this.props.maxHeight || DEFAULT_MAX_HEIGHT,
        }}
      >
        {hasMore && (
          <ShowMoreHandle>
            <Button intent="primary" onClick={() => this.setState({expanded: !expanded})}>
              {expanded ? 'Show less' : 'Show more'}
            </Button>
          </ShowMoreHandle>
        )}

        <div ref={this._container} style={{overflowX: 'auto'}}>
          <Markdown>{removeLeadingSpaces(this.props.description)}</Markdown>
        </div>
      </Container>
    );
  }
}

const Container = styled.div<{$fontSize: string | number}>`
  overflow: hidden;
  position: relative;
  font-size: ${({$fontSize}) => (typeof $fontSize === 'number' ? `${$fontSize}px` : $fontSize)};
  p:last-child {
    margin-bottom: 0;
  }

  & code,
  & pre {
    font-size: ${({$fontSize}) => (typeof $fontSize === 'number' ? `${$fontSize}px` : $fontSize)};
  }
`;

const ShowMoreHandle = styled.div`
  position: absolute;
  padding: 0 14px;
  bottom: 0;
  left: 50%;
  transform: translate(-50%);
`;
