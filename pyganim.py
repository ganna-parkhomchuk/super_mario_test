import pygame
import time
from settings import PLAYING, PAUSED, STOPPED, NORTH, SOUTH, WEST, EAST, NORTH_WEST, SOUTH_WEST, \
    NORTH_EAST, SOUTH_EAST, SCREEN_START, CENTER


class PygAnimation:
    def __init__(self, frames, loop=True):
        self._images = []
        self._durations = []
        self._start_times = None
        self._transformed_images = []
        self._state = STOPPED
        self._loop = loop
        self._visibility = True

        self._elapsed = 0
        self._playing_start_time = 0
        self._paused_start_time = 0

        if frames != '_copy':
            self.num_frames = len(frames)
            assert self.num_frames > 0, 'Must  contain at least one frame.'
            for i in range(self.num_frames):
                frame = frames[i]
                # assert type(frame) in (list, tuple) and len(frame) == 2, 'Frame %s has incorrect format.' % i
                # assert type(frame[0]) in (str, pygame.Surface), 'Frame %s image must be a string ' \
                #                                                 'filename or a pygame.Surface.' % i
                # assert type(frame[1]) > 0, 'Frame %s duration must be greater than zero .' % i
                # assert type(frame[1]) > 0, 'Frame {} duration must be greater than zero .'.format(i)
                assert type(frame) in (list, tuple) and len(frame) == 2, 'Frame {} has incorrect format.'.format(i)
                assert type(frame[0]) in (str, pygame.Surface), 'Frame {} image must be a string filename or a pygame. ' \
                                                                'Surface'.format(i)
                assert frame[1] > 0, 'Frame %s duration must be greater than zero.'.format(i)
                if type(frame[0]) == str:
                    frame = (pygame.image.load(frame[0]), frame[1])
                self._images.append(frame[0])
                self._durations.append((frame[1]))
            self._start_times = self._get_start_times()

    def _get_start_times(self):
        start_times = [0]
        for i in range(self.num_frames):
            start_times.append(start_times[-1] + self._durations[i])
        return start_times

    def reversed(self):
        self._elapsed = self._start_times[-1] - self._elapsed
        self._images.reverse()
        self._transformed_images.reverse()
        self._durations.reverse()

    def get_copy(self):
        return self.get_copies(1)[0]

    def get_copies(self, num_copies=1):
        ret_val = []
        for i in range(num_copies):
            new_anim = PygAnimation('_copy', loop=self._loop)
            new_anim._images = self._images[:]
            new_anim._transformed_images = self._transformed_images[:]
            new_anim._durations = self._durations[:]
            new_anim._start_times = self._start_times[:]
            new_anim.num_frames = self.num_frames
            ret_val.append(new_anim)
        return ret_val

    def blit(self, dest_surface, dest):
        if self.is_finished():
            self._state = STOPPED
        if not self._visibility or self._state == STOPPED:
            return
        frame_num = find_start_time(self._start_times, self._elapsed)
        dest_surface.blit(self.get_frame(frame_num), dest)

    def get_frame(self, frame_num):
        if not self._transformed_images:
            return self._images[frame_num]
        else:
            return self._transformed_images[frame_num]

    def get_current_frame(self):
        return self.get_frame(self.get_current_frame())

    def clear_transforms(self):
        self._transformed_images = []

    def make_transforms_permanent(self):
        self._images = [pygame.Surface(surf_obj.get_size(), 0, surf_obj) for surf_obj in self._transformed_images]
        for i in range(len(self._transformed_images)):
            self._images[i].blit(self._transformed_images[i], SCREEN_START)

    def blit_frame_num(self, frame_num, dest_surface, dest):
        if self.is_finished():
            self._state = STOPPED
        if not self._visibility or self._state == STOPPED:
            return
        dest_surface.blit(self.get_frame(frame_num), dest)

    def blit_frame_at_time(self, elapsed, dest_surface, dest):
        if self.is_finished():
            self._state = STOPPED
        if not self._visibility or self._state == STOPPED:
            return
        frame_num = find_start_time(self._start_times, elapsed)
        dest_surface.blit(self.get_frame(frame_num), dest)

    def play(self, start_time=None):
        if start_time is None:
            start_time = time.time()
        if self._state == PLAYING:
            if self.is_finished():
                self._playing_start_time = start_time
        elif self._state == STOPPED:
            self._playing_start_time = start_time
        elif self._state == PAUSED:
            self._playing_start_time = start_time - (self._paused_start_time - self._playing_start_time)
            self._elapsed = start_time - self._playing_start_time

        self._state = PLAYING

    def is_finished(self):
        return not self._loop and self._elapsed >= self._start_times[-1]

    def pause(self, start_time=None):
        if start_time is None:
            start_time = time.time()

        if self._state == PAUSED:
            return
        elif self._state == PLAYING:
            self._paused_start_time = start_time
        elif self._state == STOPPED:
            right_now = time.time()
            self._playing_start_time = right_now
            self._paused_start_time = right_now
        self._state = PAUSED

    def stop(self):
        if self._state == STOPPED:
            return  # do nothing
        self._state = STOPPED

    def toggle_pause(self):
        if self._state == PLAYING:
            if self.is_finished():
                self.play()
            else:
                self.pause()
        elif self._state in (PAUSED, STOPPED):
            self.play()

    def are_frames_same_size(self):
        width, height = self.get_frame(0).get_size()
        for i in range(len(self._images)):
            if self.get_frame(i).get_size() != (width, height):
                return False
        return True

    def get_max_size(self):
        frame_widths = []
        frame_heights = []
        for i in range(len(self._images)):
            frameWidth, frameHeight = self._images[i].get_size()
            frame_widths.append(frameWidth)
            frame_heights.append(frameHeight)
        max_width = max(frame_widths)
        max_height = max(frame_heights)

        return (max_width, max_height)

    def getRect(self):
        max_width, max_height = self.get_max_size()
        return pygame.Rect(0, 0, max_width, max_height)

    def anchor(self, anchor_point=NORTH_WEST):
        if self.are_frames_same_size():
            return

        self.clear_transforms()

        max_width, max_height = self.get_max_size()
        half_max_width = int(max_width / 2)
        half_max_height = int(max_height / 2)

        for i in range(len(self._images)):
            new_surf = pygame.Surface((max_width, max_height))
            new_surf = new_surf.convert_alpha()
            new_surf.fill((0, 0, 0, 0))

            frame_width, frame_height = self._images[i].get_size()
            half_frame_width = int(frame_width / 2)
            half_frame_height = int(frame_height / 2)

            if anchor_point == NORTH_WEST:
                new_surf.blit(self._images[i], SCREEN_START)
            elif anchor_point == NORTH:
                new_surf.blit(self._images[i], (half_max_width - half_frame_width, 0))
            elif anchor_point == NORTH_EAST:
                new_surf.blit(self._images[i], (max_width - frame_width, 0))
            elif anchor_point == WEST:
                new_surf.blit(self._images[i], (0, half_max_height - half_frame_height))
            elif anchor_point == CENTER:
                new_surf.blit(self._images[i], (half_max_width - half_frame_width, half_max_height - half_frame_height))
            elif anchor_point == EAST:
                new_surf.blit(self._images[i], (max_width - frame_width, half_max_height - half_frame_height))
            elif anchor_point == SOUTH_WEST:
                new_surf.blit(self._images[i], (0, max_height - frame_height))
            elif anchor_point == SOUTH:
                new_surf.blit(self._images[i], (half_max_width - half_frame_width, max_height - frame_height))
            elif anchor_point == SOUTH_EAST:
                new_surf.blit(self._images[i], (max_width - frame_width, max_height - frame_height))
            self._images[i] = new_surf

    def next_frame(self, jump=1):
        self.current_frame_num += int(jump)

    def prev_frame(self, jump=1):
        self.current_frame_num -= int(jump)

    def rewind(self, seconds=None):
        if seconds is None:
            self.elapsed = 0.0
        else:
            self.elapsed -= seconds

    def fast_forward(self, seconds=None):
        if seconds is None:
            self.elapsed = self._start_times[-1] - 0.00002
        else:
            self.elapsed += seconds

    def _make_transformed_surfaces_if_needed(self):
        if not self._transformed_images:
            self._transformed_images = [surf.copy() for surf in self._images]

    def flip(self, x_bool, y_bool):
        self._make_transformed_surfaces_if_needed()
        for i in range(len(self._images)):
            self._transformed_images[i] = pygame.transform.flip(self.get_frame(i), x_bool, y_bool)

    def scale(self, width_height):
        self._make_transformed_surfaces_if_needed()
        for i in range(len(self._images)):
            self._transformed_images[i] = pygame.transform.scale(self.get_frame(i), width_height)

    def rotate(self, angle):
        self._make_transformed_surfaces_if_needed()
        for i in range(len(self._images)):
            self._transformed_images[i] = pygame.transform.rotate(self.get_frame(i), angle)

    def rotozoom(self, angle, scale):
        self._make_transformed_surfaces_if_needed()
        for i in range(len(self._images)):
            self._transformed_images[i] = pygame.transform.rotozoom(self.get_frame(i), angle, scale)

    def scale2x(self):
        self._make_transformed_surfaces_if_needed()
        for i in range(len(self._images)):
            self._transformed_images[i] = pygame.transform.scale2x(self.get_frame(i))

    def smoothscale(self, width_height):
        self._make_transformed_surfaces_if_needed()
        for i in range(len(self._images)):
            self._transformed_images[i] = pygame.transform.smoothscale(self.get_frame(i), width_height)

    def _surface_method_wrapper(self, wrapped_method_name, *args, **kwargs):
        self._make_transformed_surfaces_if_needed()
        for i in range(len(self._images)):
            method_to_call = getattr(self._transformed_images[i], wrapped_method_name)
            method_to_call(*args, **kwargs)

    def convert(self, *args, **kwargs):
        self._surface_method_wrapper('convert', *args, **kwargs)

    def convert_alpha(self, *args, **kwargs):
        self._surface_method_wrapper('convert_alpha', *args, **kwargs)

    def set_alpha(self, *args, **kwargs):
        self._surface_method_wrapper('set_alpha', *args, **kwargs)

    def scroll(self, *args, **kwargs):
        self._surface_method_wrapper('scroll', *args, **kwargs)

    def set_clip(self, *args, **kwargs):
        self._surface_method_wrapper('set_clip', *args, **kwargs)

    def set_colorkey(self, *args, **kwargs):
        self._surface_method_wrapper('set_colorkey', *args, **kwargs)

    def lock(self, *args, **kwargs):
        self._surface_method_wrapper('lock', *args, **kwargs)

    def unlock(self, *args, **kwargs):
        self._surface_method_wrapper('unlock', *args, **kwargs)

    def _propGetRate(self):
        return self._rate

    def _propSetRate(self, rate):
        rate = float(rate)
        if rate < 0:
            raise ValueError('rate must be greater than 0.')
        self._rate = rate

    rate = property(_propGetRate, _propSetRate)

    def _propGetLoop(self):
        return self._loop

    def _propSetLoop(self, loop):
        if self.state == PLAYING and self._loop and not loop:
            self._playing_start_time = time.time() - self.elapsed
        self._loop = bool(loop)

    loop = property(_propGetLoop, _propSetLoop)

    def _propGetState(self):
        if self.is_finished():
            self._state = STOPPED  # if finished playing, then set state to STOPPED.

        return self._state

    def _propSetState(self, state):
        if state not in (PLAYING, PAUSED, STOPPED):
            raise ValueError('state must be one of pyganim.PLAYING, pyganim.PAUSED, or pyganim.STOPPED')
        if state == PLAYING:
            self.play()
        elif state == PAUSED:
            self.pause()
        elif state == STOPPED:
            self.stop()

    state = property(_propGetState, _propSetState)

    def _propGetVisibility(self):
        return self._visibility

    def _propSetVisibility(self, visibility):
        self._visibility = bool(visibility)

    visibility = property(_propGetVisibility, _propSetVisibility)


    def _propSetElapsed(self, elapsed):
        elapsed += 0.00001
        if self._loop:
            elapsed = elapsed % self._start_times[-1]
        else:
            elapsed = get_in_between_value(0, elapsed, self._start_times[-1])

        rightNow = time.time()
        self._playing_start_time = rightNow - (elapsed * self.rate)

        if self.state in (PAUSED, STOPPED):
            self.state = PAUSED
            self._paused_start_time = rightNow

    def _propGetElapsed(self):
        # NOTE: Do to floating point rounding errors, this doesn't work precisely.

        # To prevent infinite recursion, don't use the self.state property,
        # just read/set self._state directly because the state getter calls
        # this method.

        # Find out how long ago the play()/pause() functions were called.
        if self._state == STOPPED:
            # if stopped, then just return 0
            return 0

        if self._state == PLAYING:
            # if playing, then draw the current frame (based on when the animation
            # started playing). If not looping and the animation has gone through
            # all the frames already, then draw the last frame.
            elapsed = (time.time() - self._playing_start_time) * self.rate
        elif self._state == PAUSED:
            # if paused, then draw the frame that was playing at the time the
            # PygAnimation object was paused
            elapsed = (self._paused_start_time - self._playing_start_time) * self.rate
        if self._loop:
            elapsed = elapsed % self._start_times[-1]
        else:
            elapsed = get_in_between_value(0, elapsed, self._start_times[-1])
        elapsed += 0.00001  # done to compensate for rounding errors
        return elapsed

    elapsed = property(_propGetElapsed, _propSetElapsed)

    def _propGetCurrentFrameNum(self):
        # Return the frame number of the frame that will be currently
        # displayed if the animation object were drawn right now.
        return find_start_time(self._start_times, self.elapsed)

    def _propSetCurrentFrameNum(self, frameNum):
        # Change the elapsed time to the beginning of a specific frame.
        if self.loop:
            frameNum = frameNum % len(self._images)
        else:
            frameNum = get_in_between_value(0, frameNum, len(self._images) - 1)
        self.elapsed = self._start_times[frameNum]

    current_frame_num = property(_propGetCurrentFrameNum, _propSetCurrentFrameNum)

class PygConductor(object):
    def __init__(self, *animations):
        assert len(animations) > 0, 'at least one PygAnimation object is required'

        self._animations = []
        self.add(*animations)

    def add(self, *animations):
        if type(animations[0]) == dict:
            for k in animations[0].keys():
                self._animations.append(animations[0][k])
        elif type(animations[0]) in (tuple, list):
            for i in range(len(animations[0])):
                self._animations.append(animations[0][i])
        else:
            for i in range(len(animations)):
                self._animations.append(animations[i])

    def _propGetAnimations(self):
        return self._animations

    def _propSetAnimations(self, val):
        self._animations = val

    animations = property(_propGetAnimations, _propSetAnimations)

    def play(self, startTime=None):
        if startTime is None:
            startTime = time.time()

        for animObj in self._animations:
            animObj.play(startTime)

    def pause(self, startTime=None):
        if startTime is None:
            startTime = time.time()

        for animObj in self._animations:
            animObj.pause(startTime)

    def stop(self):
        for animObj in self._animations:
            animObj.stop()

    def reverse(self):
        for animObj in self._animations:
            animObj.reverse()

    def clear_transforms(self):
        for animObj in self._animations:
            animObj.clear_transforms()

    def make_transforms_permanent(self):
        for animObj in self._animations:
            animObj.make_transforms_permanent()

    def togglePause(self):
        for animObj in self._animations:
            animObj.toggle_pause()

    def nextFrame(self, jump=1):
        for animObj in self._animations:
            animObj.next_frame(jump)

    def prevFrame(self, jump=1):
        for animObj in self._animations:
            animObj.prev_frame(jump)

    def rewind(self, seconds=None):
        for animObj in self._animations:
            animObj.rewind(seconds)

    def fastForward(self, seconds=None):
        for animObj in self._animations:
            animObj.fast_forward(seconds)

    def flip(self, xbool, ybool):
        for animObj in self._animations:
            animObj.flip(xbool, ybool)

    def scale(self, width_height):
        for animObj in self._animations:
            animObj.scale(width_height)

    def rotate(self, angle):
        for animObj in self._animations:
            animObj.rotate(angle)

    def rotozoom(self, angle, scale):
        for animObj in self._animations:
            animObj.rotozoom(angle, scale)

    def scale2x(self):
        for animObj in self._animations:
            animObj.scale2x()

    def smoothscale(self, width_height):
        for animObj in self._animations:
            animObj.smoothscale(width_height)

    def convert(self):
        for animObj in self._animations:
            animObj.convert()

    def convert_alpha(self):
        for animObj in self._animations:
            animObj.convert_alpha()

    def set_alpha(self, *args, **kwargs):
        for animObj in self._animations:
            animObj.set_alpha(*args, **kwargs)

    def scroll(self, dx=0, dy=0):
        for animObj in self._animations:
            animObj.scroll(dx, dy)

    def set_clip(self, *args, **kwargs):
        for animObj in self._animations:
            animObj.set_clip(*args, **kwargs)

    def set_colorkey(self, *args, **kwargs):
        for animObj in self._animations:
            animObj.set_colorkey(*args, **kwargs)

    def lock(self):
        for animObj in self._animations:
            animObj.lock()

    def unlock(self):
        for animObj in self._animations:
            animObj.unlock()


def get_in_between_value(lowerBound, value, upperBound):
    if value < lowerBound:
        return lowerBound
    elif value > upperBound:
        return upperBound
    return value


def find_start_time(start_times, target):
    assert start_times[0] == 0
    lb = 0
    ub = len(start_times) - 1

    if len(start_times) == 0:
        return 0
    if target >= start_times[-1]:
        return ub - 1

    while True:
        i = int((ub - lb) / 2) + lb

        if start_times[i] == target or (start_times[i] < target < start_times[i + 1]):
            if i == len(start_times):
                return i - 1
            else:
                return i

        if start_times[i] < target:
            lb = i
        elif start_times[i] > target:
            ub = i
