"""
    probability.py - all probability-related models (particle filter, ...)
"""

import math
from math import cos, sin, exp, pi, sqrt
import random
import svg

def Gaussian(mu, sigma, x):
    # calculates the probability of x for 1-dim Gaussian with mean mu and var. sigma
    return exp(- ((mu - x) ** 2) / (sigma ** 2) / 2.0) / sqrt(2.0 * pi * (sigma ** 2))

class ParticleFilter(object):
    """A particle filter that calculates localization probability
    based on a series of (noisy) measurements and displacements"""


    def __init__(self, car, map=None, initAngle = 0, numParticles = 100):
        self.car = car
        self.N = numParticles
        self.initAngle = initAngle
        self.particles = list()

        self.setMap(map)


    def setMap(self, map):
        """Sets a map for the particle filter (and executes random population)"""

        self.width = map.width
        self.height = map.height
        self.map = map
        self.populate(self.N, self.initAngle)

    def populate(self, N, objectAngle):
        """Adds N random particles to the particle filter. (Useful at initialization)"""

        for i in xrange(N):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)

            while self.map.isObstacle(x, y):
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)

            self.particles.append( Particle(x, y, angle = objectAngle, probability = 1. ) ) # / self.N  )

    def sense(self, measuredDistance, angle):
        """Updates the probabilities to match a measurement.
        Uses a Gaussian on the difference between measured and calculated distance
        and takes into account the sensor's noise.
        """

        for particle in self.particles:
            particleDist = self.map.rayDistance( particle.x, particle.y, angle )

            # TODO : particleDist should never be None (== no obstacle ahead), should be a 'max' distance
            if particleDist is None:
                particleDist = self.width + self.height

            # TODO: Same as particleDist
            if measuredDistance is None:
                measuredDistance = self.width + self.height

            particle.p *= Gaussian(particleDist, self.car.sensor_noise, measuredDistance)

    def move(self, distance, angle = 0.):
        """Updates the probabilities to match a displacement.
        Updates the particles' coordinates (taking into account 'noise')
        """

        for particle in self.particles:

            if angle != 0:
                # We update the particle's orientation
                deltaAngle = angle + random.gauss(0.0, math.radians(self.car.rotation_noise))
                particle.turnAngle(deltaAngle)

            if distance != 0:
                # ...  and it's position
                deltaDistance = distance + random.gauss(0.0, self.car.displacement_noise)
                particle.move(deltaDistance)

            # If the particle got out of the universe, we put it on the border
            particle.x = min( max(0, particle.x) , self.width )
            particle.y = min( max(0, particle.y) , self.height )

    def normalize(self):
        """Normalizes the particles's weights.
        (Makes the sum of all probabilities equal to 1)
        """
        sumProba = sum( particle.p for particle in self.particles )
        for particle in self.particles:
            particle.p /= sumProba

    def resample(self):
        """Resampling the particles using a 'resampling wheel' algorithm."""
        newParticles = list()
        maxProba = max( particle.p for particle in self.particles )
        index = random.randint(0, len(self.particles) - 1)
        B = 0.0

        for i in xrange( len(self.particles) ):
            B += random.randint(0, int(2 * maxProba))

            while self.particles[index].p < B:
                B -= self.particles[index].p
                index = (index + 1) % len(self.particles)

            newParticles.append( self.particles[index] )

        self.particles = newParticles


    def __repr__(self):
        repr = ""
        for particle in self.particles:
            repr += particle.__repr__() + '\n'

        return repr


class Particle(object):

    def __init__(self, x, y, angle = 0., probability = 1.):

        self.x, self.y = x, y
        self.angle = angle
        self.p = probability

    def turnAngle(self, deltaAngle):

        self.angle = (self.angle + deltaAngle + pi) % (2*pi) - pi

    def move(self, displacement):

        dx = displacement * cos(self.angle)
        dy = - displacement * sin(self.angle)

        self.x, self.y = int(self.x + dx) , int(self.y + dy)

    def __repr__(self):
        return '[x = {} y = {} angle = {} degree | proba = {}]'.format(self.x, self.y, int(math.degrees(self.angle)), self.p)


if __name__ == "__main__":

    myMap = svg.SvgTree("maps/mapexample.svg")

    proba = ParticleFilter(myMap, 0)

    proba.move(10, 0)
    proba.sense(204, 0)

    print proba

    proba.resample()


# x = 147.0  y = 483.0 ; angle = 0 => dist = 204
